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
    bless $self, $class;
    return $self;
}

sub is_reference_ensembl_gene_idl {
    my $self = shift;
    return $self->{_gene}->slice->is_reference();
}
# Most of the required information is contained in the hash returned by this method.
sub get_gene_detail_map {
    my $self = shift;
    unless($self->{_gene}) {
	    return {};
    }
    return $self->{_gene}->summary_as_hash;
}
1;