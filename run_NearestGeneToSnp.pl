use strict;
use warnings;
use v5.10;
use NearestGeneToSnp;
use JSON;

=head
This script was written to be called in a Python class "NearestGeneFivePrime",
see file "nearest_gene_five_prime.py".
Given a single column file that contains a list of rs IDs,
slurp in the file and get details of the nearest gene at the 5 prime
for each rs ID.

Print the output as JSON to stdout.
=cut
my $rs_id_list_file = $ARGV[0];
unless(-f $rs_id_list_file) {
    die("No such file '$rs_id_list_file'!");
}
my $file_contents;
# Slurp the file into a single string.
{
  local $/ = undef;
  open my $fh, $rs_id_list_file or die "Couldn't open file: $!";
  $file_contents = <$fh>;
  close $fh;
}
# Split the slurped file into a list where each element is an rs ID.
my @rs_ids = split(/\s+/, $file_contents);
my $rs_id_nearest_gene_map = {};
my $nearest_gene = NearestGeneToSnp->new();
# Loop through each of the rs IDs and get a list of hashes with gene distance details
# and add them to a list.
foreach my $rs_id (@rs_ids) {
    $rs_id_nearest_gene_map->{$rs_id} =
        $nearest_gene->get_five_prime_gene_map_list($rs_id)
}
# Print the list of hashes as JSON to stdout.
print encode_json($rs_id_nearest_gene_map);