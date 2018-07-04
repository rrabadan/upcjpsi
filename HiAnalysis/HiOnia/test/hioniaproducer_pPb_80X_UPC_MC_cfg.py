import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing


#----------------------------------------------------------------------------

# Setup Settings for ONIA TREE:
isZB           = False   
#isMC           = False    # if input is MONTECARLO: True or if it's DATA: False
isMC           = True    # if input is MONTECARLO: True or if it's DATA: False
applyMuonCuts  = False    # Apply muon ID quality cuts
muonSelection  = "Trk"    # Single muon selection: Glb(isGlobal), GlbTrk(isGlobal&&isTracker), Trk(isTracker) are availale
genPDG         = 443      # Generated Particle PDG ID (only needed for MC), Jpsi: 443 , Psi(2S): 100443, Upsilon(1S): 553 , Upsilon(2S): 100553 , Upsilon(2S): 200553

#----------------------------------------------------------------------------

# Print Onia Skim settings:
print( " " ) 
print( "[INFO] Settings used for ONIA TREE DATA: " )  
print( "[INFO] isMC          = " + ("True" if isMC else "False") )  
print( "[INFO] applyMuonCuts = " + ("True" if applyMuonCuts else "False") ) 
print( "[INFO] muonSelection = " + muonSelection )  
print( "[INFO] genPDG        = " + str(genPDG) )
print( " " )


# set up process
process = cms.Process("HIOnia")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# Input and Output File Names
#options.outputFile = "OniaTreePromptC.root"
outputFile = "OniaTreePromptC.root"
#options.secondaryOutputFile = "Jpsi_DataSet.root"
#options.inputFiles = 'file:/afs/cern.ch/user/a/anstahll/UPDATE/ONIA/CMSSW_8_0_23/src/HiSkim/HiOnia2MuMu/test/60F56674-D8A4-E611-A91A-FA163EB6F0FA.root'
options.maxEvents = 10000 # -1 means all events

# Get and parse the command line arguments
# options.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.categories.extend(["GetManyWithoutRegistration","GetByLabelWithoutRegistration"])
process.MessageLogger.destinations = ['cout', 'cerr']
process.MessageLogger.categories.extend(["HiOnia2MuMuPAT_muonLessSizeORpvTrkSize"])
process.MessageLogger.cerr.HiOnia2MuMuPAT_muonLessSizeORpvTrkSize = cms.untracked.PSet( limit = cms.untracked.int32(5) )

process.load('TrackingTools/TransientTrack/TransientTrackBuilder_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')

# Global Tag:
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '80X_dataRun2_Prompt_v15', '')
process.GlobalTag.snapshotTime = cms.string("9999-12-31 23:59:59.000")
if isMC:
  process.GlobalTag = GlobalTag(process.GlobalTag, '80X_mcRun2_pA_v4', '')

process.GlobalTag.toGet = cms.VPSet(
  cms.PSet(
    record = cms.string("HeavyIonRcd"),
    tag = cms.string("CentralityTable_HFtowersPlusTrunc200_EPOS5TeV_v80x01_mc"),
    connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
    label = cms.untracked.string("HFtowersPlusTruncEpos")
    ),
  cms.PSet(
    record = cms.string('L1TUtmTriggerMenuRcd'),
    tag = cms.string("L1Menu_HeavyIons2016_v2_m2_xml"),
    connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS')
    ),
  cms.PSet(
    record = cms.string('L1TGlobalPrescalesVetosRcd'),
    tag = cms.string("L1TGlobalPrescalesVetos_Stage2v0_hlt"),
    connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS')
    )
  )

### HiONIA SKIM 
# HLT Dimuon Triggers
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
# HLT pPb MENU:  /users/anstahll/PA2016/PAMuon2016Full/V3
process.hltOniaHI.HLTPaths =  [
  "HLT_PADoubleMuOpen_HFOneTowerVeto_SingleTrack_v1",
  "HLT_PADoubleMuOpen_HFOneTowerVeto_v1",
  "HLT_PADoubleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
  "HLT_PADoubleMuOpen_HFTwoTowerVeto_v1",
  "HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt10_v1",
  "HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt15_v1",
  "HLT_PASingleMuOpen_PixelTrackGt0Lt10_v1",
  "HLT_PASingleMuOpen_PixelTrackGt0Lt15_v1",
  "HLT_PASingleMuOpen_HFOneTowerVeto_SingleTrack_v1",
  "HLT_PASingleMuOpen_HFOneTowerVeto_v1",
  "HLT_PASingleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
  "HLT_PASingleMuOpen_HFTwoTowerVeto_v1",
  ]

process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True
process.hltOniaHI.TriggerResultsTag = cms.InputTag("TriggerResults","","HLT")

from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *
onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=isMC, HLT="HLT", Filter=True, useL1Stage2=True)


### Temporal fix for the PAT Trigger prescale warnings.
process.patTriggerFull.l1GtReadoutRecordInputTag = cms.InputTag("gtDigis","","RECO") #?
process.patTriggerFull.l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis","","RECO")   #?
process.patTriggerFull.l1tExtBlkInputTag = cms.InputTag("gtStage2Digis","","RECO")   #?
process.patTriggerFull.getPrescales      = cms.untracked.bool(True)                  #?
###

##### Onia2MuMuPAT input collections/options
process.onia2MuMuPatGlbGlb.dimuonSelection          = cms.string("mass > 1.5 && mass < 9.0")
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity   = True
process.onia2MuMuPatGlbGlb.srcTracks                = cms.InputTag("generalTracks")
process.onia2MuMuPatGlbGlb.primaryVertexTag         = cms.InputTag("offlinePrimaryVertices")
process.patMuonsWithoutTrigger.pvSrc                = cms.InputTag("offlinePrimaryVertices")
# Adding muonLessPV gives you lifetime values wrt. muonLessPV only
process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = True
if isMC:
  process.genMuons.src = "genParticles"
  process.onia2MuMuPatGlbGlb.genParticles = "genParticles"

##### Dimuon pair selection
commonP1 = "|| (innerTrack.isNonnull && genParticleRef(0).isNonnull)"
commonP2 = " && abs(innerTrack.dxy)<4 && abs(innerTrack.dz)<35"
if muonSelection == "Glb":
  highP = "isGlobalMuon"; # At least one muon must pass this selection
  process.onia2MuMuPatGlbGlb.higherPuritySelection = cms.string("("+highP+commonP1+")"+commonP2)
  lowP = "isGlobalMuon"; # BOTH muons must pass this selection
  process.onia2MuMuPatGlbGlb.lowerPuritySelection = cms.string("("+lowP+commonP1+")"+commonP2)
elif muonSelection == "GlbTrk":
  highP = "(isGlobalMuon && isTrackerMuon)";
  process.onia2MuMuPatGlbGlb.higherPuritySelection = cms.string("("+highP+commonP1+")"+commonP2)
  lowP = "(isGlobalMuon && isTrackerMuon)";
  process.onia2MuMuPatGlbGlb.lowerPuritySelection = cms.string("("+lowP+commonP1+")"+commonP2)
elif muonSelection == "Trk":
  highP = "isTrackerMuon";
  process.onia2MuMuPatGlbGlb.higherPuritySelection = cms.string("("+highP+commonP1+")"+commonP2)
  lowP = "isTrackerMuon";
  process.onia2MuMuPatGlbGlb.lowerPuritySelection = cms.string("("+lowP+commonP1+")"+commonP2)
else:
  print "ERROR: Incorrect muon selection " + muonSelection + " . Valid options are: Glb, Trk, GlbTrk"

##### Remove few paths for MC
if isMC:
  process.patMuonSequence.remove(process.hltOniaHI)


### For Centrality
##original
'''process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.load("RecoHI.HiEvtPlaneAlgos.hiEvtPlaneFlat_cfi")
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("pACentrality")
process.centralityBin.centralityVariable = cms.string("HFtowersPlusTrunc")
process.centralityBin.nonDefaultGlauberModel = cms.string("Epos")
process.hiEvtPlaneFlat.vertexTag = cms.InputTag("offlinePrimaryVertices")
process.hiEvtPlaneFlat.centralityTag = cms.InputTag("pACentrality")
process.hiEvtPlaneFlat.centralityBinTag = cms.InputTag("centralityBin","HFtowersPlusTrunc")
process.hiEvtPlaneFlat.centralityVariable = cms.string("HFtowersPlusTrunc")
process.hiEvtPlaneFlat.nonDefaultGlauberModel = cms.string("Epos")
process.hiEvtPlane.vertexTag = cms.InputTag("offlinePrimaryVertices")
process.hiEvtPlane.centralityBinTag = cms.InputTag("centralityBin","HFtowersPlusTrunc")
process.hiEvtPlane.centralityVariable = cms.string("HFtowersPlusTrunc")
process.hiEvtPlane.nonDefaultGlauberModel = cms.string("Epos")
process.EventAna_step = cms.Path( process.centralityBin * process.hiEvtPlane * process.hiEvtPlaneFlat )'''
## A la Javier
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("pACentrality")
process.centralityBin.centralityVariable = cms.string("HFtowersPlusTrunc")
process.centralityBin.nonDefaultGlauberModel = cms.string("Epos")
process.EventAna_step = cms.Path( process.centralityBin )

process.load("HiAnalysis.HiOnia.QWZDC_cfi")
process.load("HiAnalysis.HiOnia.HFMaxCaloTowerProducer_cfi")

### HiOnia Analyzer 
process.hionia = cms.EDAnalyzer('HiOniaAnalyzer',
                                #-- Collections
                                srcMuon             = cms.InputTag("patMuonsWithTrigger"),     # Name of PAT Muon Collection
                                srcMuonNoTrig       = cms.InputTag("patMuonsWithoutTrigger"),  # Name of PAT Muon Without Trigger Collection
                                # onia2MuMuPatGlbGlb / onia2MuMuPatTrkTrk
                                src                 = cms.InputTag("onia2MuMuPatGlbGlb"),      # Name of Onia Skim Collection
                                EvtPlane            = cms.InputTag("hiEvtPlane",""),           # Name of Event Plane Collection. For RECO use: hiEventPlane,recoLevel
                                Trak                = cms.InputTag("selectedPatTrackCands"), #clean

                                triggerResultsLabel = cms.InputTag("TriggerResults","","HLT"), # Label of Trigger Results

                                evZDCSum            = cms.InputTag("QWZDC","Sum",    ""),
                                evZDCSumN           = cms.InputTag("QWZDC","SumN",   ""),
                                evZDCSumP           = cms.InputTag("QWZDC","SumP",   ""),
                                evZDCemSumN         = cms.InputTag("QWZDC","emSumN", ""),
                                evZDCemSumP         = cms.InputTag("QWZDC","emSumP", ""),
                                evZDChadSumN        = cms.InputTag("QWZDC","hadSumN",""),
                                evZDChadSumP        = cms.InputTag("QWZDC","hadSumP",""),
                                
                                evMaxHF             = cms.InputTag("hfmaxcalotower","maxHFen",   ""),
                                evMaxHFN            = cms.InputTag("hfmaxcalotower","maxHFNen",  ""),
                                evMaxHFP            = cms.InputTag("hfmaxcalotower","maxHFPen",  ""),
                                evMaxHFeta          = cms.InputTag("hfmaxcalotower","maxHFeta",  ""),
                                evMaxHFphi          = cms.InputTag("hfmaxcalotower","maxHFphi",  ""),

                                #-- Reco Details
                                useBeamSpot = cms.bool(False),  
                                useRapidity = cms.bool(True),
                                
                                #--
                                maxAbsZ = cms.double(24.0),
                                
                                pTBinRanges      = cms.vdouble(0.0, 6.0, 8.0, 9.0, 10.0, 12.0, 15.0, 40.0),
                                etaBinRanges     = cms.vdouble(0.0, 2.5),
                                centralityRanges = cms.vdouble(20,40,100),
                                
                                onlyTheBest        = cms.bool(False),
                                applyCuts          = cms.bool(applyMuonCuts),
                                selTightGlobalMuon = cms.bool(False),
                                storeEfficiency    = cms.bool(False),
                      
                                removeSignalEvents = cms.untracked.bool(False),  # Remove/Keep signal events
                                removeTrueMuons    = cms.untracked.bool(False),  # Remove/Keep gen Muons
                                storeSameSign      = cms.untracked.bool(False),   # Store/Drop same sign dimuons
                                
                                #-- Gen Details
                                oniaPDG = cms.int32(genPDG),
                                muonSel = cms.string(muonSelection),
                                isHI = cms.untracked.bool(False), ###
                                isPA = cms.untracked.bool(True),
                                isMC = cms.untracked.bool(isMC),
                                isPromptMC = cms.untracked.bool(False),  ###
                                useEvtPlane = cms.untracked.bool(False), ###
                                useGeTracks = cms.untracked.bool(False),
                                runVersionChange = cms.untracked.uint32(182133),

                                #-- Histogram configuration
                                combineCategories = cms.bool(False),
                                fillRooDataSet    = cms.bool(False),
                                fillTree          = cms.bool(True),
                                fillHistos        = cms.bool(False), #TRUE
                                minimumFlag       = cms.bool(False),
                                fillSingleMuons   = cms.bool(True),
                                fillRecoTracks    = cms.bool(True),
                                #histFileName      = cms.string(options.outputFile),   
                                histFileName      = cms.string(outputFile),   
                                dataSetName       = cms.string(options.secondaryOutputFile),


                                ################### ZDC ###################
                                isZB = cms.untracked.bool(isZB),
                                Src = cms.untracked.InputTag("castorDigis"),
                                Src_towerMaker = cms.untracked.InputTag("towerMaker"),
                                Src_rechits = cms.untracked.InputTag("hfreco"),
                                ###########################################

                                # dE/dX
                                # dEdx1Tag = cms.InputTag('dedxHarmonic2'),
                                # dEdx2Tag = cms.InputTag('dedxDiscrimASmi'),
                                # HLT pPb MENU:  /users/anstahll/PA2016/PAMuon2016Full/V3
                                
                                
                                dblTriggerPathNames = cms.vstring("HLT_PADoubleMuOpen_HFOneTowerVeto_SingleTrack_v1",
                                                                  "HLT_PADoubleMuOpen_HFOneTowerVeto_v1",
                                                                  "HLT_PADoubleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
                                                                  "HLT_PADoubleMuOpen_HFTwoTowerVeto_v1",
                                                                  "HLT_PAL1DoubleMu0_v1",
                                                                  "HLT_PAL1DoubleMuOpen_OS_v1",
                                                                  "HLT_PAL1DoubleMuOpen_v1"),

                                dblTriggerFilterNames = cms.vstring("hltL1fL1shltUPCL1DoubleMuOpenHFOneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1DoubleMuOpenHFOneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1DoubleMuOpenNotHF0TwoTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1DoubleMuOpenNotHF0TwoTowerFiltered0",
                                                                    "hltL1fL1sDoubleMu0BptxANDL1Filtered0",
                                                                    "hltL1fL1sDoubleMuOpenOSBptxANDL1Filtered0",
                                                                    "hltL1fL1sDoubleMuOpenBptxANDL1Filtered0"),

                                sglTriggerPathNames = cms.vstring("HLT_PASingleMuOpen_v1",
                                                                  "HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt10_v1",
                                                                  "HLT_PASingleMuOpen_PixelTrackGt0_FullTrackLt15_v1",
                                                                  "HLT_PASingleMuOpen_PixelTrackGt0Lt10_v1",
                                                                  "HLT_PASingleMuOpen_PixelTrackGt0Lt15_v1",
                                                                  "HLT_PASingleMuOpen_HFOneTowerVeto_SingleTrack_v1",
                                                                  "HLT_PASingleMuOpen_HFOneTowerVeto_v1",
                                                                  "HLT_PASingleMuOpen_HFTwoTowerVeto_SingleTrack_v1",
                                                                  "HLT_PASingleMuOpen_HFTwoTowerVeto_v1"),

                                sglTriggerFilterNames = cms.vstring("hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0OneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0OneTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0TwoTowerFiltered0",
                                                                    "hltL1fL1shltUPCL1SingleMuOpenNotHF0TwoTowerFiltered0")
                                )

process.hionia.primaryVertexTag = cms.InputTag("offlinePrimaryVertices")
process.hionia.genParticles     = cms.InputTag("genParticles")
process.hionia.muonLessPV       = cms.bool(True)
process.hionia.EvtPlane         = cms.InputTag("hiEvtPlaneFlat","")
process.hionia.CentralitySrc    = cms.InputTag("pACentrality")
process.hionia.CentralityBinSrc = cms.InputTag("centralityBin","HFtowersPlusTrunc")
process.hionia.srcTracks        = cms.InputTag("generalTracks")

#Options:
process.source    = cms.Source("PoolSource",
                               #fileNames = cms.untracked.vstring( options.inputFiles )
                               fileNames = cms.untracked.vstring( 
    '/store/hidata/PARun2016C/PAForward/AOD/PromptReco-v1/000/285/517/00000/2E19C083-2CB0-E611-8B63-02163E011905.root',
    #'/store/hidata/PARun2016C/PAForward/AOD/PromptReco-v1/000/285/517/00000/2E31B17F-2CB0-E611-8193-FA163E4C426A.root',
    #'/store/hidata/PARun2016C/PAForward/AOD/PromptReco-v1/000/285/517/00000/2EAB237A-2CB0-E611-9753-FA163EAF1F45.root',
    # RUN 286496
    #'root://cmsxrootd.fnal.gov//store/hidata/PARun2016C/PAForward/AOD/PromptReco-v1/000/286/496/00000/F083B881-88BD-E611-B604-02163E0146EB.root',
    #'root://cmseos.fnal.gov///store/user/rrabadan/UPC8TeVMC/excJpsiSlope/ExclusiveJpsi/NoFilters-AODSIM/180331_212848/0000/starlight_RECO_1.root'
   )
)
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
#process.Onia2MuMuPAT = cms.Path(
#   process.patDefaultSequence*
#   process.patMuonSequence *
#   process.onia2MuMuPatGlbGlb *
#   process.onia2MuMuPatGlbGlbFilter *
#   process.hionia
#)

## check the event content 
#process.content = cms.EDAnalyzer("EventContentAnalyzer")

# the onia2MuMu path
#process.Onia2MuMuPAT = cms.Path(
#        process.patTrackSequence*
#        process.patMuonSequence*
#        process.onia2MuMuPatGlbGlb
        #process.onia2MuMuPatGlbGlbFilter*
        #process.content
        #process.hionia
        #        process.content
#)

process.TFileService = cms.Service("TFileService", 
                                   #fileName = cms.string( options.outputFile )
                                   fileName = cms.string( outputFile )
                                   )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.options   = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
#process.source.fileNames      = cms.untracked.vstring(options.inputFiles)
#process.p         = cms.Path(process.patDefaultSequence)
process.zdc       = cms.Path(process.QWZDC)
process.hfmax     = cms.Path(process.hfmaxcalotower)
process.p         = cms.Path(process.hionia)

#process.schedule  = cms.Schedule( process.EventAna_step, process.p )
#process.schedule  = cms.Schedule( process.EventAna_step, process.Onia2MuMuPAT )
#process.schedule  = cms.Schedule( process.p)
process.schedule  = cms.Schedule( process.Onia2MuMuPAT, process.EventAna_step, process.zdc, process.hfmax, process.p)
#process.SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",ignoreTotal = cms.untracked.int32(1000) )
