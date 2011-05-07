#! /usr/bin/perl 
#
# Based on nwsxml.pl by Lucien Dunning
#
use strict;
#use utf8;
#use open qw(:std :utf8);
use XML::SAX::PurePerl;
use XML::Simple;
use LWP::Simple;
use Getopt::Std;
use Date::Manip;
use File::Basename;
use lib dirname($0);

our ($opt_v, $opt_t, $opt_T, $opt_l, $opt_u, $opt_d); 
my $name = 'dwfd.pl';
my $version = 0.03;
my $author = 'Victor Bron';
my $email = 'mordoor@mail.ru';
my $updateTimeout = 120*60;
my $retrieveTimeout = 30;
my @types = ('3dlocation', '6dlocation',  'updatetime', 
        'high-0', 'high-1', 'high-2', 'high-3', 'high-4', 'high-5',
        'low-0', 'low-1', 'low-2', 'low-3', 'low-4', 'low-5',
        'icon-0', 'icon-1', 'icon-2', 'icon-3', 'icon-4', 'icon-5',
        'date-0', 'date-1', 'date-2', 'date-3', 'date-4', 'date-5');


my $dir = "./";
#=========================================================================================
 sub cityname_by_id{ 
  my  $id=$_[0];
  my $xs = new XML::Simple;
  my $xml = $xs->XMLin("city_list.xml",forcearray=>1);
  # print Dumper($xml)
  for  (my $i=0; $xml->{city}->[$i]->{id} !=''; ++$i) {
    if ($id==$xml->{city}->[$i]->{id}) {
      return $xml->{city}->[$i]->{name_en}[0]; 
    }  
  }
  return "N/A";
 }    
#=========================================================================================
sub dataout
{
 my @dates;
 my $w_pict;
 my $locid=$_[0];
 my $base_url;
 my $local_base_url ='http://xml.weather.co.ua/1.2/forecast/';
# my $local_base_url ='http://weather.co.ua/xml/feed.xml?version=1.0&city=';
 $base_url =$local_base_url . $locid . "?&dayf=5&userid=yorsite_com";
#m$locid";
 my $response = get $base_url; 
 die unless defined $response;
 my $xs = new XML::Simple;
 my $xml = $xs->XMLin($response,forcearray=>0);
 if (!$xml) {
    die "Not xml";
 }
 my $location =  cityname_by_id($locid);
 printf "3dlocation::" . $location . "\n"; 
 printf "6dlocation::" . $location . "\n";
 printf "updatetime::Last Updated on %s\n", 
 UnixDate($xml->{current}->{last_updated}, "%b %d, %I:%M %p %Z");
  my $j=0;
  for  (my $i=0; $i<=19; ++$i) {
  if ($xml->{forecast}->{day}[$i]->{hour}=='15'){
    my $dt=$xml->{forecast}->{day}[$i]->{date};
    my $hr=$xml->{forecast}->{day}[$i]->{hour};
    my $min_t=$xml->{forecast}->{day}[$i]->{t}->{min};
    my $max_t=$xml->{forecast}->{day}[$i]->{t}->{max};
    my $ico=$xml->{forecast}->{day}[$i]->{pict};
     if ($ico=~ /^_0_moon.gif$/i){
      $w_pict="sunny.png";}
     elsif ($ico=~ /^_0_sun.gif$/i){
      $w_pict="sunny.png";}
     elsif ($ico=~ /^_1_moon_cl.gif$/i){
      $w_pict="pcloudy.png";}
     elsif ($ico=~ /^_1_sun_cl.gif$/i){
      $w_pict="pcloudy.png";}
     elsif ($ico=~ /^_2_cloudy.gif$/i) {
      $w_pict="mcloudy.png";}
     elsif ($ico=~ /^_3_pasmurno.gif$/i) {
       $w_pict="cloudy.png";}
     elsif ($ico=~ /^_4_short_rain.gif$/i) {
      $w_pict="lshowers.png";}
     elsif ($ico=~ /^_5_rain.gif$/i) {
      $w_pict="showers.png";}
     elsif ($ico=~ /^_6_lightning.gif$/i) {
      $w_pict="thunshowers.png";}
     elsif ($ico=~ /^_7_hail.gif$/i) {
      $w_pict="fog.png";}
     elsif ($ico=~/^_8_rain_snow.gif$/i) {
      $w_pict="rainsnow.png";}
     elsif ($ico=~ /_9_snow.gif$/i) {
      $w_pict="snowshow.png";}
     elsif ($ico=~ /^_255_NA.gif$/i) {
      $w_pict="unknown.png";}
     else {
      $w_pict="unknown.png";}
      
    print "high-$j\:\:$max_t\nicon-$j\:\:$w_pict\nlow-$j\:\:$min_t\n";
    my $numdate = UnixDate($dt, "%Q");
    if (!grep /$numdate/, @dates) {
        push @dates, $numdate;
    }
    $j++;
  }
  }
  print "high-5\:\:N/A\nicon-5\:\:unknown.png\nlow-5\:\:N/A\n";  
  $j=0;
  foreach my $date (sort(@dates)) {
    print "date-${j}::" . UnixDate($date, "%A") . "\n" 
    if ($j <= 5);
    $j++;
  }
  print "date-${j}::N/A\n";
} 
#==========================================================================================

getopts('Tvtlu:d:');

if (defined $opt_v) {
    print "$name,$version,$author,$email\n";
    exit 0;
}

if (defined $opt_T) {
    print "$updateTimeout,$retrieveTimeout\n";
    exit 0;
}

if (defined $opt_l) {
    my $search = shift;
    my $s_url='http://xml.weather.co.ua/1.2/city/?search='.$search; 
    my $response = get $s_url; 
    die unless defined $response;
    my $xml = XMLin($response,forcearray=>1);
    if (!$xml) {
     die "Not xml";
    }
    for  (my $i=0; $xml->{city}->[$i]->{id} !=''; ++$i) {
     my $city_id=$xml->{city}->[$i]->{id};
     my $city_name=$xml->{city}->[$i]->{name}[0];
     printf "$city_id\:\:$city_name\n";
    }
    exit 0;
}

if (defined $opt_t) {
    foreach (@types) {print; print "\n";}
    exit 0;
}

if (defined $opt_d) {
    $dir = $opt_d;
}


 my $locid = shift;
 if (!(defined $opt_u && defined $locid && !$locid eq "")) {
    die "Invalid usage - sample ./dwfd -u SI 16 ";
 }
 else 
 {
   dataout($locid,"");
 }
