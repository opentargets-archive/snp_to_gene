=head1 NAME
  parse_input.pl

=head1 DESCRIPTION
  
  Parse file supplied by EVA & GWAS to extract rsIDs and/or coordinates

=pod
  
=head1 AUTHOR/MAINTAINER

gonzaleza@ebi.ac.uk

=cut
use strict;
use warnings;
use v5.10;
use Carp qw(confess);
package FileToList;

my $file = $ARGV[0];

my %ids;

confess("File not readable!")if(! -r $file);
open (FILE, $file) or confess("Unable to open file: $!");

while(<FILE>){
    # skipped NT expansion variants
    next if($_=~/NT expansion/);
    chomp $_;
    my ($chr, $start, $end, $ref, $alt, $strand, $sv_type, $rs_id, $rcv_id, $ncbi_gene_id, $nsv_id, $misc) = split /\s+/, $_;

    if($rs_id =~/^rs/ and !exists($ids{$rs_id})){
	    $ids{rs_id} = 1;
    }elsif($rs_id =~/\-1/){
        my $str = '1';
        $str    = '-1' if($strand =~/\-/);
        my $coord = $chr.":".$start."-".$end.":".$str."/".$alt;
        if(!exists($ids{coord})){
            $ids{coord} = 1;
        }
      }
}
close FILE;
	
print "$_\n" for keys %ids;

