#!/usr/bin/env python
#
# Copyright (c) 2016 10X Genomics, Inc. All rights reserved.
#
# Code to plot molecule length histogram and the kmer spectrum

import martian

## this function plots a normalized histogram
def plot_norm_pct_hist( plt, values, binsize, start, **plt_args ):
    x = start
    xvals = []
    yvals = []
    norm = 0.0
    for v in values:
        xvals.append(x)
        yvals.append(v)
        xvals.append(x+binsize)
        norm += v
        yvals.append(v)
        x += binsize
    for i in xrange (len(yvals)):
        yvals[i] = yvals[i]/norm*100.0
    plt.plot( xvals, yvals, **plt_args)
    plt.xlim( start, x )

def try_plot_molecule_hist(args):
    try:
        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt
        import json
        import numpy as np
        from statsmodels.nonparametric.smoothers_lowess import lowess

        ## final plot name
        plot_name = os.path.join( args.parent_dir, "stats",
                                  "molecule_lengths.pdf" )
        mol_fn = os.path.join( args.parent_dir, "stats",
                               "histogram_molecules.json" )
        mol_dict = json.loads(open( mol_fn, "r" ).read())
        if mol_dict["numbins"] > 0:
            xmin = 0     ## min length kb
            xmax = 300   ## max length kb
            binsize=1    ## bin size of hist in kb
            ## compute length-weighted histogram
            lwhist = []
            for x, v in enumerate( mol_dict["vals"] ):
               lwhist.append( (x + 0.5)* v )
            ## truncate
            lwhist = lwhist[:xmax]
            ## normalize
            norm = sum(lwhist)
            lwhist = np.array([100*x/norm for x in lwhist])
            ## lowess smoothing
            xvalues = np.arange(0, xmax, 1) + 0.5
            newhist = lowess(lwhist, xvalues, frac=0.1, return_sorted=False)
            ## do the plotting
            fig, ax = plt.subplots()
            ## set up axis, grid
            ax.grid(True)
            plt.locator_params( 'x', nbins=10 )
            plt.locator_params( 'y', nbins=10 )
            plt.plot ( newhist, **{"lw": 2, "ls": "-", "color": "blue"} )
            plt.xlim( xmin, xmax )
            plt.ylim( 0, None )
            plt.xlabel ( "Inferred molecule length (kb)")
            plt.ylabel ( "Percent of total DNA mass (1 kb bins)")
            plt.title ("Length-weighted histogram (LOWESS-smoothed)")
            plt.savefig( plot_name )
            plt.close()
    except ImportError, e:
        martian.log_info( "Error importing libraries for plotting" )
        martian.log_info( str(e) )
    except KeyError, e:
        martian.log_info( "Invalid key in json while plotting" )
        martian.log_info( str(e) )
    except IOError, e:
        martian.log_info( "Could not find the molecule json for plotting" )
        martian.log_info( str(e) )
    except Exception as e:
        martian.log_info( "Unexpected error while plotting molecule length")
        martian.log_info( str(e) )

## take a set of (distinct) numbers and format them into a list of strings
## where we have an integer followed by a suffix
## picks out the representation that has the shortest length
def nice_labels ( numbers ):
    suffixes = ['', 'K', 'M', 'G']
    suff_len = []
    ## figure out which suffix gives us the shortest label length
    for i, suff in enumerate( suffixes ):
        test   = [float(y)/(1000.0**i) for y in numbers]
        labels = ["%d%s"% (int(y), suff) for y in test]
        ## make sure that in the new representation there are no
        ## degenerate cases
        if len(set(labels)) == len(labels):
            suff_len.append( (sum(map(len, labels)), i) )
    ## if we fail to find any satisfactory suffixes, just use defaults
    if len(suff_len) == 0:
        return map(str, numbers), 0
    else:
        suff_len.sort()
        i = suff_len[0][1]
        labels = ["%d%s"% (int(float(y)/(1000.0**i)), suffixes[i]) for y in numbers]
    return labels, i

def try_plot_kmer_spectrum(args):
    try:
        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt
        import json

        ## final plot name
        plot_name = os.path.join( args.parent_dir, "stats",
                                  "kmer_spectrum.pdf" )
        kmer_fn = os.path.join( args.parent_dir, "stats",
                               "histogram_kmer_count.json" )
        data = json.loads(open( kmer_fn, "r" ).read())
        ## max k-mer multiplicity
        MAX = 100
        if len( data["vals"] ) == 0:
            martian.log_info ("No kmer data to plot.")
            return
        elif len( data["vals"] ) < MAX:
            martian.log_info ("Warning: no kmers with multiplicity >= %d"%MAX )
            MAX = len( data["vals"] )
        fig, ax = plt.subplots()
        #plt.setp(ax.get_yticklabels(), visible=False)
        ## set mode to 1.0
        xvals = range(MAX)
        yvals = data["vals"][:MAX]
        ax.plot (xvals, yvals, lw = 2.0, color="blue" )
        ## plot tail
        tail_height = float(sum(data["vals"][MAX:]))
        _, ymax = plt.ylim()
        plt.axvspan (xmin=MAX-1, xmax=MAX, ymin=0, ymax=tail_height/ymax, ls=None, color="blue")
        ## set up axis, grid
        ax.grid(True)
        plt.locator_params( 'x', nbins=10 )
        plt.locator_params( 'y', nbins=10 )
        plt.xlim(0, MAX)
        yt = ax.get_yticks()
        ylabels, yexp = nice_labels( yt )
        plt.yticks ( yt, ylabels, rotation=45 )
        plt.xlabel ( "filtered kmer multiplicity" )
        plt.ylabel ( "counts" )
        plt.savefig (plot_name)
        plt.close()
    except ImportError, e:
        martian.log_info( "Error importing libraries for plotting" )
        martian.log_info( str(e) )
    except KeyError, e:
        martian.log_info( "Invalid key in json while plotting" )
        martian.log_info( str(e) )
    except IOError, e:
        martian.log_info( "Could not find the kmer count json for plotting" )
        martian.log_info( str(e) )
    except Exception as e:
        martian.log_info( "Unexpected error while plotting kmer spectrum")
        martian.log_info( str(e) )


