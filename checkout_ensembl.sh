#!/bin/sh --

## We use the script_dir variable to run a sister script below
script_dir=$(dirname $0)

## The first option to the script is the location for the checkout
dir=$1
if [ -z "$dir" ]; then
    echo "Usage: $0 <dir> [branch]" 1>&2
    exit 1
fi

## The second option is the branch to use (master by default)
## Note, if branch doesn't exist, it falls back to master (typically)
branch="master"
if [ ! -z "$2" ]; then
    branch="$2"
fi

## We don't rename the remote from the default (origin) on clone, but
## I'm paranoid, so I'm open to the idea that it could change...
remote=origin

## BEGIN

dir=$(readlink -f $dir)
if [ ! -e "$dir" ]; then
    echo "Directory $dir does not exist - creating..." 1>&2
    mkdir -p $dir
fi

echo "Creating Ensembl work directory in $dir"
echo

cd $dir

## First checkout the Ensembl modules that follow the standard
## branching pattern...
for module in \
    ensembl \
    ensembl-compara \
    ensembl-variation
    #ensembl-funcgen \
    #ensembl-io \
    #ensembl-production \
    #ensembl-rest \
    #ensembl-tools \
do
    echo "Checking out $module ($branch)"
    git clone -b $branch https://github.com/Ensembl/${module} || {
        echo "Could not check out $module ($branch)" 1>&2
        exit 2
    }
    echo
    echo
done


## Now checkout Hive
branch="version/2.3"
for module in \
    ensembl-hive
do
    echo "Checking out $module ($branch)"
    git clone -b $branch https://github.com/Ensembl/${module} || {
        echo "Could not check out $module ($branch)" 1>&2
        exit 2
    }
    echo
    echo
done

## Now checkout analysis and pipeline (no release branch!)
branch="master"
for module in \
    #ensembl-analysis \
    #ensembl-pipeline \
    #ensembl-taxonomy
do
    echo "Checking out $module ($branch)"
    git clone -b $branch https://github.com/Ensembl/${module} || {
        echo "Could not check out $module ($branch)" 1>&2
        exit 2
    }
    echo
    echo
done

## Gasp!

echo "Checkout complete"
#echo "Creating a setup script"

#$script_dir/create_setup_script.sh $dir

echo
echo "DONE!"
