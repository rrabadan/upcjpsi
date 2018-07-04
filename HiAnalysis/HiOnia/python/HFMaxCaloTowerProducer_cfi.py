import FWCore.ParameterSet.Config as cms

hfmaxcalotower = cms.EDProducer("HFMaxCaloTowerProducer",
    caloTowerTag = cms.untracked.InputTag("towerMaker")
)
