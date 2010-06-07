#! /usr/bin/perl -w
#This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author Viktor Malyna #
# Parts based on nwsxml.pl and dwfd.pl #
#

use strict;
use XML::Simple;
use LWP::Simple;
use LWP::UserAgent;
#use Data::Dumper;
use Date::Manip;
use Getopt::Std;

my $ua = LWP::UserAgent->new;
$ua->agent("Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)");
$ua->default_header('Host' => "xml.weather.co.ua");
$ua->default_header('Accept' => "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
$ua->default_header('Accept-Language' => "ru-ru,ru;q=0.5");
$ua->default_header('Connection' => "close");
$ua->timeout(5);
$ua->env_proxy;

my $name = 'WCUA-XML';
my $version = 0.2;
my $author = 'Viktor Malyna';
my $email = 'vicktorm@bk.ru';
my $updateTimeout = 120*60;
my $retrieveTimeout = 30;
my @types = ('cclocation', 'station_id', 'copyright', 'observation_time', 
		'weather', 'temp', 'relative_humidity', 'wind_dir', 'pressure',
		'visibility', 'weather_icon', 'appt', 'wind_spdgst', 
	    '3dlocation', 
        	'date-0', 'icon-0', 'low-0', 'high-0',
        	'date-1', 'icon-1', 'low-1', 'high-1', 
        	'date-2', 'icon-2', 'low-2', 'high-2', 'updatetime',
	    '6dlocation', 
		'date-3', 'icon-3', 'low-3', 'high-3',
        	'date-4', 'icon-4', 'low-4', 'high-4',
        	'date-5', 'icon-5', 'low-5', 'high-5', 
		);
my $dir = "./";

our ($opt_v, $opt_t, $opt_T, $opt_l, $opt_u, $opt_d);

sub getCloudStr {
    my $ncloud = $_[0];
    $ncloud /= 10;
    if ($ncloud == 0) { return "Sunny" }
    elsif ($ncloud == 1) { return "Partly Sunny " }
    elsif ($ncloud == 2) { return "Cloudy" }
    elsif ($ncloud == 3) { return "Mostly Cloudy" }
    elsif ($ncloud == 4) { return "Short Rain" }
    elsif ($ncloud == 5) { return "Rain" }
    elsif ($ncloud == 6) { return "Lighting" }
    elsif ($ncloud == 7) { return "Hail" }
    elsif ($ncloud == 8) { return "Rain Snow" }
    elsif ($ncloud == 9) { return "Snow" }
    elsif ($ncloud == 10) { return "Heavy Snow" }
    elsif ($ncloud == 25) { return "N/A" }
}

sub getWeatherIcon {
    my $img = $_[0];
    if ($img =~ /^_0_moon.gif$/i) { return "sunny.png"; }
    elsif ($img =~ /^_0_sun.gif$/i) { return "sunny.png"; }
    elsif ($img =~ /^_1_moon_cl.gif$/i) { return "pcloudy.png"; }
    elsif ($img =~ /^_1_sun_cl.gif$/i) { return "pcloudy.png"; }
    elsif ($img =~ /^_2_cloudy.gif$/i) { return "mcloudy.png"; }
    elsif ($img =~ /^_3_pasmurno.gif$/i) { return "cloudy.png"; }
    elsif ($img =~ /^_4_short_rain.gif$/i) { return "lshowers.png"; }
    elsif ($img =~ /^_5_rain.gif$/i) { return "showers.png"; }
    elsif ($img =~ /^_6_lightning.gif$/i) { return "thunshowers.png"; }
    elsif ($img =~ /^_7_hail.gif$/i) { return "fog.png"; }  
    elsif ($img =~/^_8_rain_snow.gif$/i) { return "rainsnow.png"; }
    elsif ($img =~ /_9_snow.gif$/i) { return "snowshow.png"; }
    elsif ($img =~ /^_255_NA.gif$/i) { return "unknown.png"; }
    else { return "unknown.png"; }
}

sub getWindDir {
    my $wdir = $_[0];
    if ($wdir == 255 || $wdir == 0) {return("N/A")}
    elsif ($wdir <= 20) {return("N")}
    elsif ($wdir <= 35) {return("N-N-E")}
    elsif ($wdir <= 55) {return("N-E")}  
    elsif ($wdir <= 70) {return("E-N-E")}  
    elsif ($wdir <= 110) {return("E")}
    elsif ($wdir <= 125) {return("E-S-E")}
    elsif ($wdir <= 145) {return("S-E")}
    elsif ($wdir <= 160) {return("S-S-E")}
    elsif ($wdir <= 200) {return("S")}  
    elsif ($wdir <= 215) {return("S-S-W")}
    elsif ($wdir <= 235) {return("S-W")}
    elsif ($wdir <= 250) {return("W-S-W")}
    elsif ($wdir <= 290) {return("W")}  
    elsif ($wdir <= 305) {return("W-N-W")}  
    elsif ($wdir <= 325) {return("N-W")}
    elsif ($wdir <= 340) {return("N-N-W")}
    elsif ($wdir <= 360) {return("N")}
}

#
# Main Program
#

# parse command line arguments 
getopts('Tvtlu:d:');

# option v  -  script informations
if (defined $opt_v) {
    print "$name,$version,$author,$email\n";
    exit 0;
}

# option T  -  delay values
if (defined $opt_T) {
    print "$updateTimeout,$retrieveTimeout\n";
    exit 0;
}
# option l - search location
if (defined $opt_l) {
    my ($search) = shift;

    my $response = $ua->get("http://xml.weather.co.ua/1.2/city/?search=" . $search);
	    die unless defined $response;
    my $xml = XMLin($response->decoded_content, ForceArray => 1);

    if (!$xml) {
	die "Not xml";
    }

    foreach my $item (@{$xml->{city}}) {
	printf "%s::%s", $item->{id},  $item->{name_en}->[0] . "\n";
    }
    exit 0;
}

# Option t  - give used items
if (defined $opt_t) {
    foreach (@types) {print; print "\n";}
    exit 0
}

# Option d  - defined the directory for the cache
if (defined $opt_d) {
    $dir = $opt_d;
}

# we get here, we're doing an actual retrieval, everything must be defined
my $cityid = shift;
if (!(defined $opt_u && defined $cityid && !$cityid eq "")) {
    die "Invalid usage: $0 -u SI <city id>\n";
}

my $units = $opt_u;

# http://xml.weather.co.ua/1.2/forecast/23?dayf=5&userid=yoursite_co
my $base_url = 'http://xml.weather.co.ua/1.2/forecast/';

my $response = $ua->get($base_url . $cityid . "?dayf=5&userid=yoursite_co&lang=ru");
    die unless defined $response; 

my $xml = XMLin($response->decoded_content, ForceArray => 0);

if (!$xml) {
    die "Not xml";
}

# The required elements which aren't provided by this feed
printf "copyright::From weather.co.ua\n";
printf "station_id::" . $cityid . "\n";
printf "cclocation::" . $xml->{city}->{name_en} . ", " . $xml->{city}->{country}->{name_en} . "\n";
printf "observation_time::" . $xml->{current}->{time} . "\n";
printf "weather::" . getCloudStr($xml->{current}->{cloud}) . "\n";
printf "weather_icon::" . getWeatherIcon($xml->{current}->{pict}) . "\n";
printf "temp::" . $xml->{current}->{t} . "\n";
printf "appt::" . $xml->{current}->{t_flik} . "\n";
printf "wind_dir::" . getWindDir($xml->{current}->{w_rumb}) . "\n";
printf ("%s::%4.1f%s", "wind_spdgst", $xml->{current}->{w} * 3.6, "\n"); 
printf "relative_humidity::" . $xml->{current}->{h} . "\n"; 
printf ("%s::%4.f%s", "pressure", $xml->{current}->{p} * 1.33, "\n");
printf "visibility::N/A\n";

# Data is the 3d and 6d forecast
printf "3dlocation::" . $xml->{city}->{name_en} . ", " . $xml->{city}->{country}->{name_en} . "\n";
printf "6dlocation::" . $xml->{city}->{name_en} . ", " . $xml->{city}->{country}->{name_en} . "\n";

my $i = 0;
my $k = 0;
my %hour_15;
my %hour_3;

foreach my $nday (@{$xml->{forecast}->{day}}) {
    if (defined($nday->{hour}) && ($nday->{hour} eq '15')) {
	$hour_15{$i} = [$nday->{date}, getWeatherIcon($nday->{pict}), $nday->{t}->{max}, $nday->{t}->{min}];
	$i++;
    }
    if (defined($nday->{hour}) && $nday->{hour} eq '3') {
	$hour_3{$k} = [$nday->{date}, getWeatherIcon($nday->{pict}), $nday->{t}->{max}, $nday->{t}->{min}];
	$k++
    }
}

while (my ($key, $value) = each (%hour_15)) {
    printf "date-" . $key . "::" . UnixDate($value->[0], "%d.%m\t%A") . "\n";
    printf "icon-" . $key . "::" . $value->[1] . "\n";
    printf "high-" . $key . "::" . $value->[2] . "\n";
    my $lowtemp = $value->[3]; 
    while (my ($hkey, $hvalue) = each (%hour_3)) {
	if ($value->[0] eq $hvalue->[0]) {
	    $lowtemp = $hvalue->[3];
	}
    }
     printf "low-" . $key . "::" . $lowtemp . "\n";
}

if (keys %hour_15 < keys %hour_3) {
    printf "date-4::" . UnixDate($hour_3{4}->[0], "%d.%m\t%A") . "\n";
    printf "icon-4::" . $hour_3{4}->[1] . "\n";
    printf "high-4::" . $hour_3{4}->[2] . "\n";
    printf "low-4::" . $hour_3{4}->[3] . "\n";
}
elsif (keys %hour_15 > keys %hour_3) {
    printf "date-5::" . UnixDate($hour_15{4}->[0], "%d.%m\t%A") . "\n";
    printf "icon-5::" . $hour_15{4}->[1] . "\n";
    printf "high-5::" . $hour_15{4}->[2] . "\n";
    printf "low-5::" . $hour_15{4}->[3] . "\n";
}
printf "updatetime::" . $xml->{current}->{last_updated} . "\n";
printf "date-5::N/A\n";
printf "icon-5::unknown.png\n";
printf "low-5::N/A\n";
printf "high-5::N/A\n";