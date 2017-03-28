use strict;
use warnings;
use v5.10;
use Variant;
use FileToList;
use JSON;

=head
Print a JSON that maps rs ID to a Boolean (0 and 1) indicating
if the rs ID is present in the current Ensembl.
Test on local machine:
$ perl /Users/mmaguire/PycharmProjects/snp_to_gene/variants_in_ensembl.pl  \
       /Users/mmaguire/PycharmProjects/snp_to_gene/test_data/rs_id_list.txt
May need to set PERL5LIB.
=cut
my $rs_id_list_file = $ARGV[0];
my $file_to_list = FileToList->new($rs_id_list_file);
my $rs_ids = $file_to_list->get_lines_as_list();
my %variant_in_ensembl_map;
foreach my $rs_id (@$rs_ids) {
    my $variant = Variant->new($rs_id);
    $variant_in_ensembl_map{$rs_id} = $variant->is_variant_in_ensembl();
}
print  encode_json(\%variant_in_ensembl_map);