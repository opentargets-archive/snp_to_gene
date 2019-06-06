use strict;
use warnings;
use Data::Dumper;
use Bio::EnsEMBL::Registry;
use HTTP::Tiny;
use Time::HiRes;
use JSON;
use NearestGeneToSnp;

my $rs_id = "rs116768843";

my $nearest_gene = NearestGeneToSnp->new();
my @nearest_gene = $nearest_gene->get_five_prime_nearest_gene($rs_id);

if(scalar(@$nearest_gene) > 0){
                my $gene_id      = @$nearest_gene[0]->{ensembl_gene_id};
                my $gene_symbol  = @$nearest_gene[0]->{external_name};
                my $consequence  = 'nearest_gene_five_prime_end';
                my $distance  = @$nearest_gene[0]->{distance};

                print "$id\t$in_ensembl\t$gene_id\t$gene_symbol\t$consequence\t$distance\n";
} else { print "$id\t$in_ensembl\tNo nearest_gene_five_prime_end found!\n"; }