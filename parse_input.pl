=head1 NAME
  parse_input.pl

=head1 DESCRIPTION
  
  Parse file supplied by EVA & GWAS to extract rsIDs and/or coordinates
  by EVA & GWAS

=pod
  
=head1 AUTHOR/MAINTAINER

gonzaleza@ebi.ac.uk

=cut
use strict;
use warnings;
use v5.10;
use Carp qw(confess);
package FileToList;

sub new {
    my $class          = shift;
    my $full_file_path = shift;

    my $self = {};
    $self->{full_file_path} = $full_file_path;
    bless $self, $class;
return $self;
}

=head2 get_lines_as_list
    
  Ensure that the file is readable,
  parse the file, pull required columns
  and put them into format required by 
  VEP endpoint. 
 
  * Use rs_id as first option
 
  Return a reference to array

=cut
sub get_lines_as_list {
    my $self = shift;
    my @ids;

    confess("File not readable!")if(! -r $self->{full_file_path}); 
    open (FILE, $self->{full_file_path}) or confess("Unable to open file: $!");

    while(<FILE>){
      # skipped NT expansion variants	 
      next if($_=~/NT expansion/);
      chomp $_;
      my ($chr, $start, $end, $ref, $alt, $strand, $sv_type, $rs_id, $rcv_id, $ncbi_gene_id, $nsv_id, $misc) = split /\s+/, $_;

      if($rs_id =~/^rs/){
	push @ids, $rs_id
      }elsif($rs_id =~/\-1/){
        my $str = '1';
        $str    = '-1' if($strand =~/\-/);
        my $coord = $chr.":".$start."-".$end.":".$str."/".$alt;       
        push @ids, $coord;
      } 
    }
    close FILE;
	
return \@ids;
}

# Does the same but deals only
# with file with single columns of rs_id
sub get_lines_as_list_old {
    my $self = shift;

    my $file_contents;
    if(! -r $self->{full_file_path}) {
        confess("File not readable!");
    }
    {
        local $/ = undef;
        open my $fh, $self->{full_file_path} or confess("Unable to open file: $!");
        $file_contents = <$fh>;
        close $fh;
    }
    # Split the slurped file into a list where each element is an rs ID.
    my @lines = split(/\s+/, $file_contents);
    return \@lines;
}
1;
