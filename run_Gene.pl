use strict;
use warnings;
use v5.10;
use Gene;
use Data::Dumper qw(Dumper);
# Gene name AGER. Ths gene has multiple non-reference Ensembl gene IDs
my @ensembl_gene_ids = qw(ENSG00000204305 ENSG00000206320 ENSG00000229058 );

foreach my $ensembl_gene_id (@ensembl_gene_ids) {
    my $ager_gene = Gene->new($ensembl_gene_id);
    say $ager_gene->get_external_name();
    say $ager_gene->get_ensembl_gene_id_for_reference();
}