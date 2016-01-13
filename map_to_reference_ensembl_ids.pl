use strict;
use warnings;
use v5.10;
use Gene;
use JSON;

my @ensembl_gene_ids = @ARGV;
@ensembl_gene_ids = grep { $_ =~ /^ENSG/} @ensembl_gene_ids;
my %ensembl_reference_id_map;

foreach my $ensembl_gene_id (@ensembl_gene_ids) {
    my $ager_gene = Gene->new($ensembl_gene_id);
    my $external_name = $ager_gene->get_external_name();
    my $ensembl_gene_id_for_reference = $ager_gene->get_ensembl_gene_id_for_reference();
    my %details;
    $details{external_name} = $external_name;
    $details{ensembl_gene_id_for_reference} = $ensembl_gene_id_for_reference;
    $ensembl_reference_id_map{$ensembl_gene_id} = \%details;
}
print encode_json(\%ensembl_reference_id_map);
