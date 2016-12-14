=head1 NAME
  FileToList.pm

=head1 DESCRIPTION
  
  Module that handle parsing of snp file supply 
  by EVA & GWAS

=pod
  
=head1 AUTHOR/MAINTAINER

ckong@ebi.ac.uk

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
  and made them into format required by 
  VEP endpoint. 
  
  Return a reference to array

=cut
sub get_lines_as_list {
    my $self = shift;
    my @coord_str;

    confess("File not readable!")if(! -r $self->{full_file_path}); 
    open (FILE, $self->{full_file_path}) or confess("Unable to open file: $!");

    while(<FILE>){
      chomp $_;
      	my ($chr, $start, $end, $ref, $alt, $rs_id, $rcv_id, $ncbi_gene_id, $strand) = split /\t/, $_;
        my $coord_str = $chr.":".$start."-".$end.":".$strand."/".$alt;       
        push @coord_str, $coord_str;
    } 
    close FILE;
	
return \@coord_str;
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
