#!/usr/bin/env perl
=head1 NAME
 snp_assignment.pl

=head1 DESCRIPTION

 Given a file with variant IDs and/or coordinates information
 get gene assignment and required information (SO terms etc) 
 using Ensembl Perl API and VEP REST endpoint.

 Methods Overview:

 1: Check if the input variants are in the current Ensembl.
 2: Get gene assignment of variants, from VEP REST endpoint. 
    (only protein-coding with most severe consequence)
 3: For intergenic variants (e.g. ~35% of GWAS Catalog),
    no VEP output, assign to nearest protein-coding gene at the 5' end.

 Output TSV-separated file, columns are:

 1: Input rs_id/coordinates
 2: In Ensembl check (1 for yes, 0 for no)
 3: Ensembl gene stable ID
 4: Gene symbol
 5: SO term
 6: Distance to nearest gene at 5’ (0 for intragenic variants)

 limit to 15 requests per second but also look for the 'Retry-After' header
 to ensure they are not rate limited due to shared IP addresses.

=pod
  
=head1 AUTHOR

ckong@ebi.ac.uk

=head1 MAINTAINERS

gonzaleza@ebi.ac.uk
faulcon@ebi.ac.uk

=cut
use strict;
use warnings;
use Data::Dumper;
use Bio::EnsEMBL::Registry;
use HTTP::Tiny;
use Time::HiRes;
use JSON;
use NearestGeneToSnp;

my $registry = 'Bio::EnsEMBL::Registry';

$registry->set_reconnect_when_lost(1);

$registry->load_registry_from_db(
    # alternatively 'useastdb.ensembl.org'
    -host => 'ensembldb.ensembl.org', 
    -user => 'anonymous',
);

my $gene_adaptor = $registry->get_adaptor('human', 'core', 'gene' );
my $var_adaptor  = $registry->get_adaptor('human', 'variation', 'variation');

my $file          = $ARGV[0];
my $request_count = 0;
my $last_request_time = Time::HiRes::time();

# Read variants from file
open (FILE, $file) or confess("Unable to open file: $!");

while(my $id = <$FILE>){

   chomp $id;

   my $in_ensembl = '1';

   # check rs_id status
   if($id =~/^rs/){
     my $var   = $var_adaptor->fetch_by_name($id);
     $in_ensembl = defined($var) ? 1 : 0;  
   }

   if($in_ensembl){
   	my $json        = _GetVepData($id);
   	my $arr_of_hash = decode_json($json);
	# e.g. rs876660862, rs869320723
    if(ref($arr_of_hash) ne 'ARRAY'){
        if($arr_of_hash->{error}){
            print "$id\t$in_ensembl\tNA\tNA\t[VEP ERROR] $arr_of_hash->{error}\tNA\n";
        }else{
            print "$id\t$in_ensembl\tNA\tNA\t[VEP Error] Alleles look like an insertion\tNA\n" ;
        }
        next;
    }

   	foreach my $entry (@$arr_of_hash){
   	    my $most_severe_consequence = $entry->{most_severe_consequence};
      	my $rs_id   = $entry->{id};

		# arr_of_hash
		my $flag    = 0;
      	my $tr_cons = $entry->{transcript_consequences};

      	foreach my $entry_2 (@$tr_cons) {
	 	    my $gene_id     = $entry_2->{gene_id};
	 	    my $gene_symbol = $entry_2->{gene_symbol};
 	 	    my $biotype     = $entry_2->{biotype};
	 	    my @terms       = @{$entry_2->{consequence_terms}};
	 	    my $terms       = join ",", @terms;
		    my $distance    = 0;
		    # obtain gene with 'most_severe_consequence'
            next unless ($biotype =~/protein_coding/ || $biotype =~/miRNA/);

	 	    if(grep(/$most_severe_consequence/, @terms)){
		        print "$id\t$in_ensembl\t$gene_id\t$gene_symbol\t$most_severe_consequence\t$distance\n";
	 	    }
		    $flag = 1 if($biotype =~/protein_coding/);
     	}

        # e.g rs869025300
        # revisit snp assign to miRNA gene,
        # to get nearest protein_coding genes as well
        if($most_severe_consequence=~/\?/ || $most_severe_consequence=~/intergenic_variant/ || $flag==0){
            my $nearest_gene = _NearestGeneToSnp($rs_id);

            if(scalar(@$nearest_gene) > 0){
                my $gene_id      = @$nearest_gene[0]->{ensembl_gene_id};
                my $gene_symbol  = @$nearest_gene[0]->{external_name};
                my $consequence  = 'nearest_gene_five_prime_end';
                my $distance  = @$nearest_gene[0]->{distance};
                        
                print "$id\t$in_ensembl\t$gene_id\t$gene_symbol\t$consequence\t$distance\n";
            } else { print "$id\t$in_ensembl\tNo nearest_gene_five_prime_end found!\n"; }
        }
  	}    
  } 
  else { print "$id\t$in_ensembl\tVariant NOT found in Ensembl\n"; }

}

=head2 _GetVepData

 Return a JSON for VEP results of variant identifiers 

=cut
sub _GetVepData {
    my ($id) = @_;

    my $http   = HTTP::Tiny->new();
    my $server = 'https://rest.ensembl.org';
    my $ext;

    if($id =~/^rs/){
       $ext = '/vep/human/id/';
    }else {
       $ext = '/vep/human/region/';
    }
    $ext = $ext.$id."?";

    if($request_count == 15) { # check evey 15
	my $current_time = Time::HiRes::time();
        my $time_diff    = $current_time - $last_request_time;

        # sleep for remainder of the sec
        # if $time_diff less than 1 sec
	Time::HiRes::sleep(1-$time_diff) if($time_diff < 1);

        # reset timer
        $last_request_time = Time::HiRes::time();
        $request_count = 0 ;
    }
  
    my $response = $http->get($server.$ext, {
    	headers => { 'Content-type' => 'application/json' }
    });

    my $status = $response->{status};

    if(!$response->{success}){
        # check for rate limit exceeded & retry-after
        #  HTTP Response code 429 =>
        #  'Too Many Request, You have been rate-limited; wait and retry.'

        my $current_time_string = localtime();

	    if($status == 429 && exists $response->{headers}->{'retry-after'}) {
		    print STDERR "[$current_time_string] HTTP ERROR 429 calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";
		    print STDERR "*** RETRYING ***\n\n";

		    my $retry = $response->{headers}->{'retry-after'};
      	    Time::HiRes::sleep($retry);
      	    # after sleeping re-request
		    return _GetVepData($id);
        } elsif($status == 429) {
            print STDERR "[$current_time_string] HTTP ERROR 429 calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";
		    print STDERR "*** RETRYING ***\n\n";

            # Wait random time between 1 and 10 seconds before retrying
            Time::HiRes::sleep(1.0+rand(9));
            # after sleeping re-request
            return _GetVepData($id);
        } elsif($status == 400){
            print STDERR "[$current_time_string] HTTP ERROR 400 calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";

            # No return needed here, the default ones outside the if will be used

        } elsif($status == 504) {
            print STDERR "[$current_time_string] HTTP ERROR 504 calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";
		    print STDERR "*** RETRYING ***\n\n";

            # Wait random time between 1 and 10 seconds before retrying
            Time::HiRes::sleep(1.0+rand(9));
            # after sleeping re-request
            return _GetVepData($id);
        } elsif($status == 503) {
            print STDERR "[$current_time_string] HTTP ERROR 503 calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";
		    print STDERR "*** RETRYING ***\n\n";

            # Wait random time between 1 and 10 seconds before retrying
            Time::HiRes::sleep(1.0+rand(9));
            # after sleeping re-request
            return _GetVepData($id);
 	    }elsif($status == 500){
 	        print STDERR "[$current_time_string] HTTP ERROR 500 calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";
		    print STDERR "*** RETRYING ***\n\n";

 	        # Wait random time between 1 and 10 seconds before retrying
            Time::HiRes::sleep(1.0+rand(9));
            # after sleeping re-request
            return _GetVepData($id);
 	    }elsif($status == 502){
 	        print STDERR "[$current_time_string] HTTP ERROR 502 calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";
		    print STDERR "*** RETRYING ***\n\n";

 	        # Wait random time between 1 and 10 seconds before retrying
            Time::HiRes::sleep(1.0+rand(9));
            # after sleeping re-request
            return _GetVepData($id);
 	    }else {
		    print STDERR "[$current_time_string] HTTP ERROR calling VEP with $id\n";
		    print STDERR "[STATUS] $response->{status}\n";
		    print STDERR "[REASON] $response->{reason})\n";
		    print STDERR "[CONTENT] $response->{content} \n";
		    print STDERR "*** RETRYING ***\n\n";

 	        # Wait random time between 1 and 10 seconds before retrying
            Time::HiRes::sleep(1.0+rand(9));
            # after sleeping re-request
            return _GetVepData($id);

		    #my ($status, $reason) = ($response->{status}, $response->{reason});
		    #return $response->{content} if(length $response->{content});
      	    #die "Failed for $id! Status code: ${status}. Reason: ${reason}\n";
        }
   }	
	
  $request_count++;
  return $response->{content} if(length $response->{content});

return;
}

=head2 _NearestGeneToSnp

 Return list of nearest gene at 5 prime for each rs_id
 
=cut
sub _NearestGeneToSnp {
    my ($rs_id) = @_;

    my $nearest_gene = NearestGeneToSnp->new();
    my @nearest_gene = $nearest_gene->get_five_prime_nearest_gene($rs_id);

return \@nearest_gene;
}


1;


