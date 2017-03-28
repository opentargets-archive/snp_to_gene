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
    -user => 'anonymous',
    -port => '3337' # for GRCh37 assembly,
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

# Returns true if the Gene object is on the reference assembly.
# Default Gene object to check is the one created in the constructor
# but a different Gene object can also be passed.
sub is_reference_ensembl_gene_id {
    my $self = shift;
    my $gene = shift || $self->{_gene};
    if( defined $gene) {
        return $gene->slice->is_reference();
    }
    return undef;
}

# Most of the required information is contained in the hash returned by this method.
# Default Gene object to check is the one created in the constructor
# but a different Gene object can also be passed.
sub get_gene_detail_map {
    my $self = shift;
    my $gene = shift || $self->{_gene};
    unless( defined $gene) {
	    return {};
    }
    return $gene->summary_as_hash;
}

# Return the external name (HGNC-recognised symbol) for the gene object created in the constructor.
sub get_external_name {
    my $self = shift;
    if( defined $self->{_gene}) {
        return $self->{_gene}->summary_as_hash->{'Name'};
    }
    return undef;
}

# Returns an Ensembl gene ID.
# Checks if the Ensembl gene ID used to create the Gene object is on the reference assembly. If yes, return it.
# If no, get all the Gene objects for the external name and return the Ensembl ID for the first that is from the
# reference assembly.
# A small number of genes have no reference assembly, example HLA-DRB3, see:
# http://www.ensembl.org/Homo_sapiens/Gene/Alleles?g=ENSG00000231679;r=CHR_HSCHR6_MHC_COX_CTG1:32444128-32521486
# For such genes, simply return the Ensembl gene passed to the constructor.
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
