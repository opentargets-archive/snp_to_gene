use strict;
use warnings;
use v5.10;
use Data::Dump "pp";
use Bio::EnsEMBL::Registry;

=head

=cut
package NearestGeneToSnp;
my $registry = 'Bio::EnsEMBL::Registry';
$registry->load_registry_from_db(
    -host => 'ensembldb.ensembl.org', # alternatively 'useastdb.ensembl.org'
    -user => 'anonymous'
);
my $gene_adaptor = $registry->get_adaptor( 'Human', 'Core', 'Gene' );
my $var_adaptor = $registry->get_adaptor( 'human', 'variation', 'variation' );
# Pass an Ensembl gene ID to the constructor that uses this to create an Ensembl gene
# instance variable.
sub new {
    my $class = shift;
    my $self = {};
    bless $self, $class;
    return $self;
}

# Given an RS ID for a SNP, return a list of nearest genes.
# Uses the simple get_nearestGene() method.
sub get_nearest_gene_list {
    my $self = shift;
    my $rs_id = shift;
    my $var = $var_adaptor->fetch_by_name($rs_id);
    my @ensembl_gene_ids = ();
    if(!$var) {
        return \@ensembl_gene_ids;
    }
    my $var_features = $var->get_all_VariationFeatures();
    foreach my $var_feature (@{$var_features}) {
          push(@ensembl_gene_ids, $var_feature->get_nearest_Gene()->stable_id);
    }
    return \@ensembl_gene_ids;
}
# http://www.ensembl.org/info/docs/Doxygen/core-api/classBio_1_1EnsEMBL_1_1DBSQL_1_1BaseFeatureAdaptor.html#a76a51bc70828aaccb9435eda9a44b20a
# Given a SNP RS ID, return a list of hashes where each maps Ensembl gene ID, gene symbol and distance from SNP.
sub get_five_prime_gene_map_list {
    my $self = shift;
    my $rs_id = shift;
    my $feature;
    my $distance;
    my @nearest_gene_map_list = ();
    my $var = $var_adaptor->fetch_by_name($rs_id);
    unless($var) {
        return \@nearest_gene_map_list;
    }
    my $var_features = $var->get_all_VariationFeatures();
    foreach my $var_feature (@{$var_features}) {
        my @gene_list_for_feature  = @{$gene_adaptor->fetch_all_by_outward_search( 
                                                           -FEATURE => $var_feature,
                                                           -RANGE => 10000,
                                                           -MAX_RANGE => 500000,
                                                           -LIMIT => 40,
                                                           -FIVE_PRIME => 1)};
        #Data::Dump::pp(\@gene_list_for_feature);
        foreach my $gene_info (@gene_list_for_feature) {
            #Data::Dump::pp(\$gene_info);
            my %nearest_gene_map;
            my $ensembl_gene_id = $gene_info->[0]->stable_id;
            my $external_name = $gene_info->[0]->external_name;
            next if $gene_info->[0]->biotype ne 'protein_coding';
            my $distance = $gene_info->[1];
            $nearest_gene_map{ensembl_gene_id} = $ensembl_gene_id;
            $nearest_gene_map{external_name} = $external_name;
            $nearest_gene_map{distance} = $distance;
            push(@nearest_gene_map_list, \%nearest_gene_map);
        }
    }
    return \@nearest_gene_map_list;
}
# Sort the list of hashes returned by "get_five_prime_gene_list()" on absolute distance from gene
# and return the list reference
sub get_five_prime_nearest_gene {
    my $self = shift;
    my $rs_id = shift;
    my $five_prime_gene_list = $self->get_five_prime_gene_map_list($rs_id);
    my @sorted = sort { abs($a->{distance}) <=> abs($b->{distance}) } @$five_prime_gene_list;
    return @sorted;
}
# Given a list of SNP RS IDs, return a hash where the keys are RS IDs and the values are
# hash refs that assign SNPs as either "intragenic" for a list of genes or as upstream for one
# gene, i.e. the nearest gene.
# This method calls "get_five_prime_nearest_gene()" for each input RS ID.
sub get_gene_assignment_for_snp_list {
    my $self = shift;
    my $snp_list = shift;
    my %snp_position_map;
    foreach my $rs_id (@$snp_list) {
        my @nearest_genes = $self->get_five_prime_nearest_gene($rs_id);
        foreach my $nearest_gene (@nearest_genes) {
            if($nearest_gene->{distance} == 0) {
                push(@{$snp_position_map{$rs_id}->{intragenic}}, $nearest_gene->{ensembl_gene_id});
            } else {
                $snp_position_map{$rs_id}->{upstream_gene_variant} = $nearest_gene->{ensembl_gene_id};
                last;
            }
        }
    }
    return \%snp_position_map;   
}
1;
