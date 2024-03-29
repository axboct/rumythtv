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
my $version = 0.3;
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
    my $ncloud = shift;
    $ncloud /= 10;
    if ($ncloud == 0) { return "Ясно"; }
    elsif ($ncloud == 1) { return "С прояснениями"; }
    elsif ($ncloud == 2) { return "Пасмурно"; }
    elsif ($ncloud == 3) { return "Перем. облачность"; }
    elsif ($ncloud == 4) { return "Небольшой дождь"; }
    elsif ($ncloud == 5) { return "Дождь"; }
    elsif ($ncloud == 6) { return "Грозы"; }
    elsif ($ncloud == 7) { return "Град"; }
    elsif ($ncloud == 8) { return "Дождь со снегом"; }
    elsif ($ncloud == 9) { return "Снег"; }
    elsif ($ncloud == 10) { return "Сильный снег"; }
    elsif ($ncloud == 25) { return "НД"; }
}

sub getWeatherIcon {
    my $img = shift;
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
    my $wdir = shift;
    if ($wdir == 255 || $wdir == 0) { return "НД"; }
    elsif ($wdir <= 20) { return "С"; }
    elsif ($wdir <= 35) {return "С-С-З"; }
    elsif ($wdir <= 55) {return "С-З"; }
    elsif ($wdir <= 70) {return "З-С-З"; }
    elsif ($wdir <= 110) {return "З"; }
    elsif ($wdir <= 125) {return "З-Ю-З"; }
    elsif ($wdir <= 145) {return "Ю-З"; }
    elsif ($wdir <= 160) {return "Ю-Ю-З";}
    elsif ($wdir <= 200) {return "Ю"; }  
    elsif ($wdir <= 215) {return "Ю-Ю-В"; }
    elsif ($wdir <= 235) {return "Ю-В"; }
    elsif ($wdir <= 250) {return "В-Ю-В"; }
    elsif ($wdir <= 290) {return "В"; }
    elsif ($wdir <= 305) {return "В-С-В"; }
    elsif ($wdir <= 325) {return "С-В"; }
    elsif ($wdir <= 340) {return "С-С-В"; }
    elsif ($wdir <= 360) {return "С"; }
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
	my $region = $item->{region}->[0];
	if (ref($region) eq "HASH") {
	    $region = "";
	}
	else {
	    $region = ", " . $region;
	}
	printf "%s::%s", $item->{id},  $item->{name}->[0] . $region . " - " . $item->{country}->[0] . "\n";
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
printf "copyright::Получено с weather.co.ua\n";
printf "station_id::" . $cityid . "\n";
printf "cclocation::" . $xml->{city}->{name} . ", " . $xml->{city}->{country}->{name} . "\n";
printf "observation_time::Обновлено - " . UnixDate(ParseDate($xml->{current}->{time}), "%d.%m.%Y, %H:%M") . "\n";
printf "weather::" . getCloudStr($xml->{current}->{cloud}) . "\n";
printf "weather_icon::" . getWeatherIcon($xml->{current}->{pict}) . "\n";
printf "temp::" . $xml->{current}->{t} . "\n";
printf "appt::" . $xml->{current}->{t_flik} . "\n";
printf "wind_dir::" . getWindDir($xml->{current}->{w_rumb}) . "\n";
printf ("%s::%d%s", "wind_spdgst", $xml->{current}->{w}, "\n");
printf "relative_humidity::" . $xml->{current}->{h} . "\n"; 
printf ("%s::%d%s", "pressure", $xml->{current}->{p}, "\n");
printf "visibility::НД\n";

# Data is the 3d and 6d forecast
printf "3dlocation::" . $xml->{city}->{name} . ", " . $xml->{city}->{country}->{name} . "\n";
printf "6dlocation::" . $xml->{city}->{name} . ", " . $xml->{city}->{country}->{name} . "\n";

my $i = 0;
my $k = 0;
my %hour_15;
my %hour_3;
my $date = 0;

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
    $date = UnixDate($value->[0], "%w");
    if ($date == 7) {
	$date = 0;
    }
    printf "date-" . $key . "::" . $date . "\n";
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
    $date = UnixDate($hour_3{4}->[0], "%w");
    if ($date == 7) {
	$date = 0;
    }
    printf "date-4::" . $date . "\n";
    printf "icon-4::" . $hour_3{4}->[1] . "\n";
    printf "high-4::" . $hour_3{4}->[2] . "\n";
    printf "low-4::" . $hour_3{4}->[3] . "\n";
}
elsif (keys %hour_15 > keys %hour_3) {
    $date = UnixDate($hour_15{4}->[0], "%w");
    if ($date == 7) {
	$date = 0;
    }
    printf "date-5::" . $date . "\n";
    printf "icon-5::" . $hour_15{4}->[1] . "\n";
    printf "high-5::" . $hour_15{4}->[2] . "\n";
    printf "low-5::" . $hour_15{4}->[3] . "\n";
}
printf "updatetime::Обновлено - " . UnixDate(ParseDate($xml->{current}->{last_updated}), "%d.%m.%Y, %H:%M") . "\n";
printf "date-5::НД\n";
printf "icon-5::unknown.png\n";
printf "low-5::НД\n";
printf "high-5::НД\n";