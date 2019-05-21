#!/usr/bin/env perl

use strict;
use warnings;
use FileToList;

my $file          = $ARGV[0];
#my $file_to_list  = FileToList->new($file);
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
print @ids."\n";