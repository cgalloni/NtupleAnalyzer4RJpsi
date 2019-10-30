# Author: Izaak Neutelings (November 2018)
import re
from corrections import ensureTFile ,modulepath

from ROOT import TFile
path = modulepath+"/pileup/"
#path="/afs/cern.ch/work/c/cgalloni/LowPtTaus_Ntuplizer/NTuplizer_UZH/CMSSW_10_2_10/src/NtupleAnalyzer4RJpsi/corrections/pileup"

class PileupWeightTool:
    
    def __init__( self, year=2017, sigma='central', sample=None, buggy=False, flat=False ):
        """Load data and MC pilup profiles."""
        
        assert( year in [2016,2017,2018] ), "You must choose a year from: 2016, 2017, or 2018."
        assert( sigma in ['central','up','down'] ), "You must choose a s.d. variation from: 'central', 'up', or 'down'."
        
        minbias = '69p2'
        if sigma=='down':
          minbias = '66p0168' # -4.6%
        elif sigma=='up':
          minbias = '72p3832' # +4.6%
        
        if year==2016:
          datafilename = path+"Data_PileUp_2016_%s.root"%(minbias)
          mcfilename   = path+"MC_PileUp_2016_Moriond17.root"
        elif year==2017:
          tag = ""
          if buggy or sample:
            buggy = buggy or hasBuggyPU(sample)
            if buggy: tag = "_old_pmx"
            else:     tag = "_new_pmx"
          datafilename = path+"Data_PileUp_2017_%s.root"%(minbias)
          mcfilename   = path+"MC_PileUp_2017_Winter17_V2%s.root"%(tag)
        else:
          datafilename = path+"Data_PileUp_2018_%s.root"%(minbias)
          mcfilename   = path+"MC_PileUp_2018_Autumn18.root"
        
        if flat or (sample and hasFlatPU(sample)):
          mcfilename   = path+"MC_PileUp_%d_FlatPU0to75.root"%year
        
        print "Loading PileupWeightTool for '%s' and '%s'"%(datafilename,mcfilename)
        self.datafile = ensureTFile(datafilename, 'READ')
        self.mcfile   = ensureTFile(mcfilename, 'READ')
        self.datahist = self.datafile.Get('pileup')
        self.mchist   = self.mcfile.Get('pileup')
        self.datahist.SetDirectory(0)
        self.mchist.SetDirectory(0)
        self.datahist.Scale(1./self.datahist.Integral())
        self.mchist.Scale(1./self.mchist.Integral())
        self.datafile.Close()
        self.mcfile.Close()
        
    
    def getWeight(self,npu):
        """Get pileup weight for a given number of pileup interactions."""
        data = self.datahist.GetBinContent(self.datahist.GetXaxis().FindBin(npu))
        mc   = self.mchist.GetBinContent(self.mchist.GetXaxis().FindBin(npu))
        if mc>0.:
          ratio = data/mc
          if ratio>5.: return 5.
          return data/mc
        print ">>> Warning! PileupWeightTools.getWeight: Could not make pileup weight for npu=%s data=%s, mc=%s"%(npu,data,mc)  
        return 1.
    

def hasBuggyPU(sample):
    """Manually check whether a given samplename has a buggy PU."""
    # BUGGY (large peak at zero nTrueInt, and bump between 2-10):
    #  /DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5_PU2017RECOSIMstep_12Apr2018_v1-DeepTauv2_TauPOG-v1/USER
    #  /DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5_PU2017RECOSIMstep_12Apr2018_ext1_v1-DeepTauv2_TauPOG-v1/USER
    #  /W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5_PU2017_12Apr2018_v1-DeepTauv2_TauPOG-v1/USER
    #  /WZ_TuneCP5_13TeV-pythia8/RunIIFall17NanoAODv5_PU2017_12Apr2018_v1-DeepTauv2_TauPOG-v1/USER
    if "RunIIFall17" in sample:
      if all(p in sample for p in ["DYJetsToLL_M-50","madgraph","pythia8","PU2017RECOSIMstep"]):
        return True
      if all(p in sample for p in ["W3JetsToLNu","madgraph","pythia8","PU2017"]):
        return True
      if all(p in sample for p in ["WZ_","pythia8","PU2017"]):
        return True
    return False
    

def hasFlatPU(sample):
    """Check whether a given samplename has a flat PU."""
    #  /DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_Fall17/RunIIFall17NanoAODv5_FlatPU0to75TuneCP5_12Apr2018_v2-DeepTauv2_TauPOG-v1/USER
    if "FlatPU0to75" in sample:
      return True
    return False
