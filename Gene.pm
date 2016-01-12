use strict;
use warnings;
use v5.10;
use Data::Dump "pp";
use Bio::EnsEMBL::Registry;

=head
Contains methods to return useful information for human genes.
=cut
package Gene;
my $registry = 'Bio::EnsEMBL::Registry';
$registry->load_registry_from_db(
    -host => 'ensembldb.ensembl.org', # alternatively 'useastdb.ensembl.org'
    -user => 'anonymous'
);
my $gene_adaptor = $registry->get_adaptor( 'Human', 'Core', 'Gene' );
# Pass an Ensembl gene ID to the constructor that uses this to create an Ensembl gene
# instance variable.
sub new {
    my $class = shift;
    my $ensembl_gene_id = shift;
    my $self = {};
    $self->{_gene} = $gene_adaptor->fetch_by_stable_id($ensembl_gene_id);
    $self->{_ensembl_gene_id} = $ensembl_gene_id;
    bless $self, $class;
    return $self;
}

sub is_reference_ensembl_gene_id {
    my $self = shift;
    my $gene = shift || $self->{_gene};
    return $gene->slice->is_reference();
}
# Most of the required information is contained in the hash returned by this method.
sub get_gene_detail_map {
    my $self = shift;
    my $gene = shift || $self->{_gene};
    unless($gene) {
	    return {};
    }
    return $gene->summary_as_hash;
}
sub get_external_name {
    my $self = shift;
    return $self->{_gene}->summary_as_hash->{'Name'};
}
sub get_ensembl_gene_id_for_reference {
    my $self = shift;
    my $external_name = $self->get_external_name();
    if($self->is_reference_ensembl_gene_id()) {
        return $self->{_ensembl_gene_id};
    }
    my @genes = @{ $gene_adaptor->fetch_all_by_external_name($external_name) };
    foreach my $gene (@genes) {
        if($self->is_reference_ensembl_gene_id($gene)) {
            return $self->get_gene_detail_map($gene)->{'id'};
        }
    }
    return $self->{_ensembl_gene_id};
}
1;