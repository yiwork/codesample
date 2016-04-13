#!/usr/bin/perl

use Net::Netmask;
use strict;

my $outfile = "~yci/ip-host.csv";
my $options = GetOptions( "o=s" => \$outfile );
my @add_space = qw|
    124.108.100.0/23
    124.108.103.0/24
    194.88.69.0/24
    217.163.21.0/24
    74.6.104.0/23
    74.6.106.0/23
    76.13.208.0/23
    76.13.210.0/23
    76.13.212.0/23
    76.13.216.0/23
    76.13.218.0/23
    76.13.220.0/23
    76.13.222.0/23
    77.238.172.0/23
    77.238.174.0/23
    98.136.74.0/23
    98.136.76.0/23
    98.136.8.0/23 |;

my @test_space = ("124.108.100.0/23");
my %networks;
foreach my $addr (@test_space) {
    my $block = new Net::Netmask( $addr );

    my @addrs = $block->enumerate();
    my $first = shift @addrs;
    my $last = pop @addrs;
    my @report;

    push (@report, "$first,,Gateway - $addr");
    foreach my $ip ( @addrs ) {
        my $search = `grep '$ip' *`;
        if ( $search ) {
            my ( $filename, $record ) = split /:/, $search;
            $record =~ /^(.*)\s+A/;
            my $hostname = $1;
            push( @report, "$ip,$filename,$hostname");
        } else {
            push( @report, "$ip,,");
        }
    }
    push (@report, "$last,,Broadcast - $addr");
    $networks{$addr} = \@report;
}

open ( FILE, ">$outfile");

foreach my $addr ( sort keys %networks ) {
print FILE join ("\n", @{ $networks{$addr} });
}

close (FILE);
