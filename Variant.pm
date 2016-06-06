use strict;
use warnings;
use v5.10;
use Data::Dump "pp";
use Bio::EnsEMBL::Registry;

=head
Contains methods to return useful information for human rs IDs.
=cut
package Variant;
my $registry = 'Bio::EnsEMBL::Registry';
$registry->load_registry_from_db(
    -host => 'ensembldb.ensembl.org', # alternatively 'useastdb.ensembl.org'
    -user => 'anonymous'
);
my $var_adaptor = $registry->get_adaptor( 'human', 'variation', 'variation' );
# Pass an Ensembl gene ID to the constructor that uses this to create an Ensembl gene
# instance variable.
sub new {
    my $class = shift;
    my $rs_id = shift;
    my $self = {};
    $self->{_rs_id} = $rs_id;
    $self->{_var} = $var_adaptor->fetch_by_name($self->{_rs_id});
    bless $self, $class;
    return $self;
}

sub is_variant_in_ensembl {
    my $self = shift;
    $self->{_var} ? 1 : 0;
}
1;