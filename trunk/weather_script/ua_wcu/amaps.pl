#!/usr/bin/perl -w
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
# Parts based on animaps.pl by Lucien Dunning #
#

use strict;
use Date::Manip;
use Image::Size;
use Getopt::Std;
use LWP::Simple;
use POSIX qw(strftime);

our ($opt_v, $opt_t, $opt_T, $opt_l, $opt_u, $opt_d);

my $name = 'MNRU-Animated-Map';
my $version = 0.1;
my $author = 'Viktor Malyna';
my $email = 'vicktorm@bk.ru';
my $updateTimeout = 10*60;
my $retrieveTimeout = 30;
my @types = ('amdesc', 'updatetime', 'animatedimage', 'copyright');
my $dir = "./";

my %location = ('Eu' => ['Ukraine', 'Украина', 'ukraine', 'украина', 'Europe', 'Европа', 'europe', 'европа'],
		'Ru' => ['Russia', 'Россия', 'russia', 'россия'],
		'Bl' => ['Belarus', 'Беларусь', 'belarus', 'беларусь'],
		'MO' => ['Central Russia', 'Центральная Россия', 'Центр России', 'central russia', 'центральная россия', 'центр россии'],
		'SSb' => ['South Simbir', 'Юг Сибири', 'Южная Сибирь', 'south simbir', 'юг сибири', 'южная сибирь']);

sub getLocation {
    my $lcode = shift;
    while (my ($key, $value) = each (%location)) {
	foreach  my $item (@{$value}) {
	    if ($item eq $lcode) {
		return $key;
		exit 0;
	    } 
	}
    }
    exit 1;
}

sub getDescription {
    my $dsc = shift;
    return 'Европа' if ($dsc eq 'Eu');
    return 'Россия' if ($dsc eq 'Ru');
    return 'Беларусь' if ($dsc eq 'Bl');
    return 'Центр России' if ($dsc eq 'MO');
    return 'Юг Сибири' if ($dsc eq 'SSb'); 
}

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
    my $loc = shift;
    if (defined ($loc) && $loc ne "") {
	my $lid = getLocation ($loc);
	print "http://www.meteonovosti.ru/maps/" . $lid . "/::" . getDescription ($lid) . "\n";
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

my $location = shift;

if (!defined $location || $location eq "") {
    die "Invalid usage: $0 -u ENG <location>\n";
}

#my $locid = getLocation ($location);
my $locid = substr ($location, 32, -1);
my $desc = getDescription ($locid);
my $base = "http://www.meteonovosti.ru/maps/" . $locid . "/";
my $date = strftime("%Y%m%d", localtime);
my $file = $desc;
my $path = "$dir/$file-";
my $url = $base . "ps_" . $locid . "_pr24_" . $date . "_00_0";
my $img = getstore ($url . "1", "/tmp/img.jpg");

if (!is_success ($img)) {
    $date = strftime("%Y%m%d", localtime (time - 86400));
    $url = $base . "ps_" . $locid . "_pr24_" . $date . "_00_0";
}
for (my $i = 1; $i < 7; $i++) {
    getstore ($url . $i . "\.jpg", $path . ($i-1));
}

my $size = '';
my ($x, $y) = imgsize("${path}0");
$size = "${x}x$y" if ($x && $y);

print "amdesc::$desc - карта погоды\n";
printf "animatedimage::${path}%%1-6%s\n", ($size && "-$size" || '');
print "updatetime::Последнее обновление - " . UnixDate("now", "%d.%m.%Y, %H:%M") . "\n";
print "copyright::Получено с сайта  www.meteonovosti.ru\n";