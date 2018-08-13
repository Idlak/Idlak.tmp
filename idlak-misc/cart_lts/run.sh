#!/bin/bash


lexicon="ga_ie_default.lex" 

echo "****() Converting lexicon"
(
cat "$lexicon" | cut -d " " -f 1-2 > converted.lex
)

phonet2cartltspath="../../idlak-misc/cart_lts/"

cd ~/idlak/tools

echo "****() Installing Phonetisaurus"
(
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
)

echo "****() Creating alignment file"
(
cd Phonetisaurus
./phonetisaurus-align \
--input="$phonet2cartltspath""converted.lex" \
--ofile="$phonet2cartltspath""ga.align" \
--delim=" " \
--s2_char_delim="_"
)
