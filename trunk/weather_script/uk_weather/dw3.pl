#! /usr/bin/perl 
#
# Based on nwsxml.pl by Lucien Dunning
#
use strict;
use XML::SAX::PurePerl;
use XML::Simple;
use LWP::Simple;
use Getopt::Std;
use File::Basename;
use lib dirname($0);

our ($opt_v, $opt_t, $opt_T, $opt_l, $opt_u, $opt_d); 
my $name = 'dwua_xml.pl';
my $version = 0.02;
my $author = 'Victor Bron';
my $email = 'mordoor@mail.ru';
my $updateTimeout = 120*60;
my $retrieveTimeout = 30;
my @types = ('cclocation', 'station_id', 'copyright',
        'observation_time', 'weather', 'temp', 'relative_humidity',
        'wind_dir', 'pressure', 'visibility', 'weather_icon',
        'appt', 'wind_spdgst', 'windchill');
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
 my $locid=$_[0];
 my $base_url;
 my $local_base_url ='http://xml.weather.co.ua/1.2/forecast/';
# my $local_base_url ='http://weather.co.ua/xml/feed.xml?version=1.0&city=';
 $base_url =$local_base_url . $locid . "?&dayf=1&userid=yoursite_com";
 my $response = get $base_url; 
 die unless defined $response;
 my $xml = XMLin($response);

if (!$xml) {
    die "Not xml";
}
 sub weather_str
 {
  my $WID=$_[0];
  if ($WID==255) {return("N/A")}
  elsif ($WID<=10) {return("Clear")}
  elsif ($WID<=20) {return("Cloudly")}
  elsif ($WID<=30) {return("Clear/Cloudly")}  
  elsif ($WID<=40) {return("Pasmurno")}  
  elsif ($WID<=50) {return("Short Rain")}
  elsif ($WID<=60) {return("Rain")}
  elsif ($WID<=70) {return("Hail")}
  elsif ($WID<=80) {return("Rain with snow")}
  elsif ($WID<=90) {return("Snow")}  
  elsif ($WID<=100) {return("Heavy Snow")} 
 }
 sub wind_dir_str
 {
  my $WID=$_[0];
  if ($WID==255) {return("N/A")}
  elsif ($WID<=20) {return("N")}
  elsif ($WID<=35) {return("NNE")}
  elsif ($WID<=55) {return("NE")}  
  elsif ($WID<=70) {return("ENE")}  
  elsif ($WID<=110) {return("E")}
  elsif ($WID<=125) {return("ESE")}
  elsif ($WID<=145) {return("SE")}
  elsif ($WID<=160) {return("SSE")}
  elsif ($WID<=200) {return("S")}  
  elsif ($WID<=215) {return("SSW")}
  elsif ($WID<=235) {return("SW")}
  elsif ($WID<=250) {return("WSW")}
  elsif ($WID<=290) {return("W")}  
  elsif ($WID<=305) {return("WNW")}  
  elsif ($WID<=325) {return("NW")}
  elsif ($WID<=340) {return("NNW")}
  elsif ($WID<=360) {return("N")}
 }


 #printf "appt::N/A\n";
 printf "copyright::(c)2005-2008 DiscoveringWeather\n";
 printf "station_id::" . $locid . "\n";
 my $location =  cityname_by_id($locid);
 printf "cclocation::" . $location . "\n";
 my $obs_time = $xml->{current}->{time};
 printf "observation_time::" . $obs_time . "\n";
 my $cloud=$xml->{current}->{cloud};
 my $weather_string = weather_str($cloud);
 printf "weather::" . $weather_string . "\n";
 my $ico=$xml->{current}->{pict};
    if ($ico=~ /^_0_moon.gif$/i){ 
    printf "weather_icon::sunny.png\n";}
    elsif ($ico=~ /^_0_sun.gif$/i){
    printf "weather_icon::sunny.png\n";}
    elsif ($ico=~ /^_1_moon_cl.gif$/i){
    printf "weather_icon::pcloudy.png\n";}
    elsif ($ico=~ /^_1_sun_cl.gif$/i){  
    printf "weather_icon::pcloudy.png\n";}
    elsif ($ico=~ /^_2_cloudy.gif$/i) {  
    printf "weather_icon::mcloudy.png\n";}
    elsif ($ico=~ /^_3_pasmurno.gif$/i) {
    printf "weather_icon::cloudy.png\n";}
    elsif ($ico=~ /^_4_short_rain.gif$/i) {
    printf "weather_icon::lshowers.png\n";}
    elsif ($ico=~ /^_5_rain.gif$/i) {
    printf "weather_icon::showers.png\n";}
    elsif ($ico=~ /^_6_lightning.gif$/i) {
    printf "weather_icon::thunshowers.png\n";}
    elsif ($ico=~ /^_7_hail.gif$/i) {
    printf "weather_icon::fog.png\n";}  
    elsif ($ico=~/^_8_rain_snow.gif$/i) {
    printf "weather_icon::rainsnow.png\n";}
    elsif ($ico=~ /_9_snow.gif$/i) {
    printf "weather_icon::snowshow.png\n";}
    elsif ($ico=~ /^_255_NA.gif$/i) {
    printf "weather_icon::unknown.png\n";}
    else {
    printf "weather_icon::unknown.png\n";}        
 my $temp = $xml->{current}->{t};
 printf "temp::$temp\n";
 my $wind_spd= $xml->{current}->{w};
 my $windchill= $xml->{current}->{t_flik};
 printf "appt::$windchill\n"; 
 my $wind_dir = wind_dir_str($xml->{current}->{w_rumb});
 my $humidity = $xml->{current}->{h};
 my $pressure = $xml->{current}->{p};
 my $visibility = "N/A";
 printf "wind_dir::$wind_dir\n";
 printf "wind_spdgst::$wind_spd\n";
 printf "relative_humidity::$humidity\n"; 
 printf "pressure::$pressure\n";
 printf "visibility::$visibility\n";
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
     my $city_name=$xml->{city}->[$i]->{name_en}[0];
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
    die "Invalid usage - sample ./dw3 -u SI 16 ";
 }
 else 
 {
   dataout($locid,"");
 }
