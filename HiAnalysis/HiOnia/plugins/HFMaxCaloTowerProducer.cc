// -*- C++ -*-
//
// Package:    HiAnalysis/testP
// Class:      testP
// 
/**\class testP testP.cc HiAnalysis/testP/plugins/testP.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  raul trejorabadan
//         Created:  Sat, 17 Mar 2018 19:28:11 GMT
//
//


// system include files
#include <memory>
#include "iostream"
#include <unordered_map>
#include <array>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "DataFormats/FWLite/interface/Handle.h"
#include "DataFormats/FWLite/interface/ChainEvent.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutRecord.h"

#include "DataFormats/CaloTowers/interface/CaloTower.h"
#include "DataFormats/CaloTowers/interface/CaloTowerFwd.h"
#include "DataFormats/CaloTowers/interface/CaloTowerCollection.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "DataFormats/CaloTowers/interface/CaloTowerDetId.h"

#include "DataFormats/EcalDetId/interface/EcalSubdetector.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/HcalRecHit/interface/HcalRecHitCollections.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"
#include "DataFormats/HcalRecHit/interface/HFRecHit.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "CalibFormats/HcalObjects/interface/HcalCalibrations.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "DataFormats/Common/interface/SortedCollection.h"
#include "DataFormats/HcalRecHit/interface/HBHERecHit.h"
#include "DataFormats/HcalRecHit/interface/HORecHit.h"
#include "DataFormats/HcalRecHit/interface/HFRecHit.h"
//#include "DataFormats/HcalRecHit/interface/ZDCRecHit.h"
//#include "DataFormats/HcalRecHit/interface/CastorRecHit.h"
#include "DataFormats/HcalRecHit/interface/HcalCalibRecHit.h"

#include "RecoJets/JetAlgorithms/interface/JetAlgoHelper.h"
#include "DataFormats/JetReco/interface/CaloJet.h"

//
// class declaration
//

class HFMaxCaloTowerProducer : public edm::stream::EDProducer<> {
   public:
      explicit HFMaxCaloTowerProducer(const edm::ParameterSet&);
      ~HFMaxCaloTowerProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginStream(edm::StreamID) override;
      virtual void produce(edm::Event&, const edm::EventSetup&) override;
      virtual void endStream() override;

      //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
      //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

      // ----------member data ---------------------------
      float MaxHFen;
      float MaxHFPen;
      float MaxHFNen;
      
      float MaxHFeta;
      float MaxHFphi;

      edm::EDGetTokenT<CaloTowerCollection>  _caloTowerToken;
};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
HFMaxCaloTowerProducer::HFMaxCaloTowerProducer(const edm::ParameterSet& iConfig):
 _caloTowerToken(consumes<CaloTowerCollection>(iConfig.getUntrackedParameter<edm::InputTag>("caloTowerTag")))
{
  produces< double >("maxHFen");
  produces< double >("maxHFPen");
  produces< double >("maxHFNen");

  produces< double >("maxHFeta");
  produces< double >("maxHFphi");
  //now do what ever other initialization is needed
}


HFMaxCaloTowerProducer::~HFMaxCaloTowerProducer()
{
  return;
   // do anything here that needs to be done at destruction time
   // (e.g. close files, deallocate resources etc.)
}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
HFMaxCaloTowerProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   using namespace std;
/* This is an event example
   //Read 'ExampleData' from the Event
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);

   //Use the ExampleData to create an ExampleData2 which 
   // is put into the Event
   std::unique_ptr<ExampleData2> pOut(new ExampleData2(*pIn));
   iEvent.put(std::move(pOut));
*/

/* this is an EventSetup example
   //Read SetupData from the SetupRecord in the EventSetup
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
*/
   MaxHFen  = -999.;
   MaxHFPen = -999.;
   MaxHFNen = -999.;
   MaxHFeta = -999.; 
   MaxHFphi = -999.;

   Handle<CaloTowerCollection>  calotower;
   iEvent.getByToken(_caloTowerToken, calotower);

   if(!calotower.failedToGet()){
     for(CaloTowerCollection::const_iterator calt=(&*calotower)->begin();calt!=(&*calotower)->end();calt++){
       bool CaloIsHF = 0;
       bool CaloIsHB = 0;
       bool CaloIsHE = 0;
       bool CaloIsEE = 0;
       bool CaloIsEB = 0;
       
       vector<DetId> detIds=calt->constituents();
       for(unsigned i = 0; i < detIds.size(); i++){
         HcalDetId hcalDetId((detIds[i].det()==DetId::Hcal)?HcalDetId(detIds[i]):HcalDetId()); 
         CaloIsHF=(CaloIsHF||(hcalDetId.subdet()==HcalForward&&detIds[i].det()==DetId::Hcal));
         CaloIsHB=(CaloIsHB||(hcalDetId.subdet()==HcalBarrel&&detIds[i].det()==DetId::Hcal));
         CaloIsHE=(CaloIsHE||(hcalDetId.subdet()==HcalEndcap&&detIds[i].det()==DetId::Hcal));
         CaloIsEB=(CaloIsEB||(EcalSubdetector(detIds[i].subdetId())==EcalBarrel&&detIds[i].det()==DetId::Ecal));
         CaloIsEE=(CaloIsEE||(EcalSubdetector(detIds[i].subdetId())==EcalEndcap&&detIds[i].det()==DetId::Ecal));
       }
       
       if(calt->energy() > MaxHFen && CaloIsHF && !CaloIsHE ) MaxHFeta = calt->p4().eta();
       if(calt->energy() > MaxHFen && CaloIsHF && !CaloIsHE ) MaxHFphi = calt->p4().phi();
       
       if(calt->energy() > MaxHFen && CaloIsHF && !CaloIsHE ) MaxHFen  = calt->energy();
       
       if(calt->energy() > MaxHFPen && CaloIsHF && !CaloIsHE &&calt->p4().eta() > 0.0) MaxHFPen = calt->energy();
       if(calt->energy() > MaxHFNen && CaloIsHF && !CaloIsHE &&calt->p4().eta() < 0.0) MaxHFNen = calt->energy();
     }
   }
   iEvent.put(auto_ptr<double>(new double(MaxHFen)),  std::string("maxHFen"));
   iEvent.put(auto_ptr<double>(new double(MaxHFPen)), std::string("maxHFPen"));
   iEvent.put(auto_ptr<double>(new double(MaxHFNen)), std::string("maxHFNen"));
   iEvent.put(auto_ptr<double>(new double(MaxHFeta)), std::string("maxHFeta"));
   iEvent.put(auto_ptr<double>(new double(MaxHFphi)), std::string("maxHFphi"));
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void
HFMaxCaloTowerProducer::beginStream(edm::StreamID)
{
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void
HFMaxCaloTowerProducer::endStream() {
}

// ------------ method called when starting to processes a run  ------------
/*
void
HFMaxCaloTowerProducer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
HFMaxCaloTowerProducer::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
HFMaxCaloTowerProducer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
HFMaxCaloTowerProducer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
HFMaxCaloTowerProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(HFMaxCaloTowerProducer);
