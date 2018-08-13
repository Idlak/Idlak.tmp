#!/bin/bash
# Takes a lexicon a generates letter-to-sound rules

if [ $# -ne 2 ]
    then
        echo "Usage is "$0" <input lexicon> <output file>"
        exit 1
    else
        lexicon=$1
        output=$2
fi

if [[ ${lexicon: -4} != ".lex" ]]
    then
        echo "Lexicon must be a .lex file"
        exit 1
fi

align="${lexicon::-4}"".align"
converted="converted.lex"

mkdir -p tmp
phonet2cartltspath="../../idlak-misc/cart_lts/tmp/"

echo "#####Converting lexicon#####"
cat "$lexicon" | cut -d " " -f 1-2 > tmp/converted.lex

cd ~/idlak/tools

echo "#####Installing Phonetisaurus#####"
if [ ! -d "Phonetisaurus" ]
then
    git clone https://github.com/AdolfVonKleist/Phonetisaurus.git
    cd Phonetisaurus
    git checkout 64719ca40c17cb70d810fffadac52c97984ca539 . || exit 1
    CXXFLAGS="-I`pwd`/../openfst/include" LDFLAGS="-Wl,-rpath=`pwd`/../openfst/lib/" \
    ./configure --with-openfst-libs=`pwd`/../openfst/lib \
        --with-openfst-includes=`pwd`/../openfst/include  \
        --prefix=`pwd`
    make -j4
    make install
else
    echo "Phonetisaurus already installed"
fi

echo "#####Creating alignment file#####"
cd Phonetisaurus
./phonetisaurus-align \
--input="$phonet2cartltspath""$converted" \
--ofile="$phonet2cartltspath""$align" \
--delim=" " \
--s2_char_delim="_"

echo "#####Generating cart files#####"
cd "$phonet2cartltspath"
python ../phonet2cart.py "$align"

echo "#####Running wagon#####"
for f in *.cart
do
    ID=${f::-5}
    mkdir -p cart/"$ID"
    wagon -desc wagon_description.dat -data "$f" -o cart/"$ID"/tree.dat
done

echo "#####Generating lts rules#####"
python ../carttree2xml.py cart ccart-default.xml
mv ccart-default.xml ..
