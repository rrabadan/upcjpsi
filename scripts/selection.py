#!/usr/bin/env python
from ROOT import *
from ROOT import TMath


def filldataset(ws,tfile,name,trgbit,realdata,goingpos):
  f = TFile(tfile,"read")  
  t = f.Get("myTree")

  effhist = TH2F()

  if realdata:
    effile  = TFile("../data/tnpanatrgfromsoftPbp.root","read")
    dataset = effile.Get("fitTriggerFromSoft/absetaptbin/fit_eff") 
    vset = dataset.get()
    xAx = vset.find("abseta")
    yAx = vset.find("pt")
    eff = vset.find('efficiency')
    effhist = TH2F("singleMuEff", "", xAx.getBinning().numBins(), xAx.getBinning().array(), yAx.getBinning().numBins(), yAx.getBinning().array())
    for i in range(dataset.numEntries()):
      dataset.get(i)
      effhist.SetBinContent(effhist.FindBin(xAx.getVal(), yAx.getVal()), eff.getVal())
      effhist.SetBinError(effhist.FindBin(xAx.getVal(), yAx.getVal()), (eff.getErrorHi() - eff.getErrorLo())/2.)
    effhist.Print("v")
    print effhist.GetNcells()

  vmass  = ws.var('mass')
  vpt    = ws.var('pt')
  vy     = ws.var('y')
  vacop  = ws.var('acop')
  vhfpl  = ws.var('hfpl')
  vhfmi  = ws.var('hfmi')
  vzdcmi = ws.var('zdcmi')

  vmumieff = ws.var('mumieff')
  vmupleff = ws.var('mupleff')

  vntk     = ws.cat('ntk')
  vtrg     = ws.cat('trig')

  obs = RooArgSet(vmass,vpt,vy,vhfmi,vhfpl)
  obs.add(vntk)
  obs.add(vtrg)
  #obs.add(vacop)
  if realdata:
    obs.add(vzdcmi)
    obs.add(vmumieff)
    obs.add(vmupleff)

  dataset = RooDataSet(name,"",obs)

  ####### Set Branches
  dimuon = TClonesArray("TLorentzVector",10)
  muonpl = TClonesArray("TLorentzVector",10)
  muonmi = TClonesArray("TLorentzVector",10)

  t.SetBranchAddress("Reco_QQ_4mom",AddressOf(dimuon))
  t.SetBranchAddress("Reco_QQ_mupl_4mom",AddressOf(muonpl))
  t.SetBranchAddress("Reco_QQ_mumi_4mom",AddressOf(muonmi))
  
  print "entries: %d" % ( t.GetEntries() )
  n = 0
  selected = 0

  for ent in t:
    n+=1
    if n%100000 == 0: print "processing entry %d" % (n)
    if ent.Reco_QQ_size != 1: continue
    if ent.Reco_mu_size != 2: continue
    if ent.Reco_QQ_VtxProb[0] < 0.01: continue
    if realdata and ent.Reco_QQ_NtrkOfPV[0] != -1: continue

    selected+=1

    mass  = ent.Reco_QQ_4mom[0].M()
    pt    = ent.Reco_QQ_4mom[0].Pt()
    y     = ent.Reco_QQ_4mom[0].Rapidity() if goingpos else -1.*ent.Reco_QQ_4mom[0].Rapidity() 
    hfpl     = ent.maxCaloTowerHFP if goingpos else ent.maxCaloTowerHFN
    hfmi     = ent.maxCaloTowerHFN if goingpos else ent.maxCaloTowerHFP
    zdcmi = ent.QWZDC_SumN
    phimi = ent.Reco_QQ_mumi_4mom[0].Phi()
    phipl = ent.Reco_QQ_mupl_4mom[0].Phi()
    dphi  = phimi - phipl;
    if dphi < -1.*TMath.Pi(): dphi =  2.*TMath.Pi() + dphi;
    if dphi >  1.*TMath.Pi(): dphi = -2.*TMath.Pi() + dphi;

    vmass.setVal(mass)
    vpt.setVal(pt)
    vy.setVal(y)
    vhfpl.setVal(hfpl)
    vhfmi.setVal(hfmi)
    vacop.setVal(ac)
    
    if realdata: 
      vzdcmi.setVal(zdcmi)
      vmupleff.setVal(effhist.GetBinContent(effhist.FindBin(abs(ent.Reco_QQ_mupl_4mom[0].Eta()),ent.Reco_QQ_mupl_4mom[0].Pt())));
      vmumieff.setVal(effhist.GetBinContent(effhist.FindBin(abs(ent.Reco_QQ_mumi_4mom[0].Eta()),ent.Reco_QQ_mumi_4mom[0].Pt())));
      #vmumieff.setVal(mumieff)
      if ent.Reco_QQ_NtrkPt1[0] == 2: vntk.setLabel('NtrkEq2')
      elif ent.Reco_QQ_NtrkPt1[0] > 2: vntk.setLabel('NtrkGt2')
      else: vntk.setLabel('Other')
    else:
      if ent.Reco_QQ_Ntrk[0] == 2: vntk.setLabel('NtrkEq2')
      elif ent.Reco_QQ_Ntrk[0] > 2: vntk.setLabel('NtrkGt2')
      else: vntk.setLabel('Other')

    if realdata: 
      vtrg.setLabel('fired')  if (ent.Reco_QQ_trig[0]>>9)&1>0  and (ent.HLTriggers>>9)&1>0  else vtrg.setLabel('notfired')
    else:
      vtrg.setLabel('notfired')
    dataset.add(obs)

  print selected
  return dataset

def fillGendataset(ws,tfile,name):
  f = TFile(tfile,"read")  
  t = f.Get("myTree")

  vmass  = ws.var('mass')
  vpt    = ws.var('pt')
  vy     = ws.var('y')

  obs = RooArgSet(vmass,vpt,vy)

  dataset = RooDataSet(name,"",obs)

  ####### Set Branches
  genmuons  = TClonesArray("TLorentzVector",10)
  gendimuon = TLorentzVector()

  t.SetBranchAddress("Gen_mu_4mom",AddressOf(genmuons))
  
  print "entries: %d" % ( t.GetEntries() )
  n = 0

  for ent in t:
    n+=1
    if n%100000 == 0: print "processing entry %d" % (n)

    gendimuon = ent.Gen_mu_4mom[0] + ent.Gen_mu_4mom[1]

    mass  = gendimuon.M()
    pt    = gendimuon.Pt()
    y     = gendimuon.Rapidity()

    vmass.setVal(mass)
    vpt.setVal(pt)
    vy.setVal(y)
    dataset.add(obs)

  return dataset

def createWorkspace():
  wspace  = RooWorkspace("w")
  massmin = 2.2
  massmax = 12.

  wspace.factory('mass[3.0,%f,%f]' % (massmin,massmax) )
  wspace.factory('y[0.0,-6.0,6.0]')
  wspace.factory('pt[2.0,0.0,10.0]')
  wspace.factory('acop[0.0,0.4]')
  wspace.factory('hfpl[0.0,100.0]')
  wspace.factory('hfmi[0.0,100.0]')
  wspace.factory('zdcmi[-100.0,200.0]')
  wspace.factory('mumieff[0.5,0.0,1.0]')
  wspace.factory('mupleff[0.5,0.0,1.0]')
  wspace.factory("ntk[NtrkEq2,NtrkGt2,Other]")
  wspace.factory("trig[fired,notfired]")

  data       = filldataset(    wspace, "../data/dimuonfwdtrkPsiMassPbp.root", "exclusivedata",    9, True, True) 
  data2      = filldataset(    wspace, "../data/dimuonfwdtrkPsiMasspPb.root", "exclusivedata2",   9, True, False) 
  recogen    = filldataset(    wspace, "../data/excjpsitkmc2.root", "psirecogendata",   9, False, True) 
  gen        = fillGendataset( wspace, "../data/excjpsitkmc2.root", "psigendata")
  gamgen     = fillGendataset( wspace, "../data/excgamgammc.root", "gamgendata")
  gamrecogen = filldataset(    wspace, "../data/excgamgammc.root", "gamrecogendata",   9, False, True) 
  #gen     = fillGendataset( wspace, "../data/excgamgammc.root", "gendata")
  
  data.Print()
  data.append(data2)
  data.Print()
  getattr(wspace,'import')(data)
  getattr(wspace,'import')(recogen)
  getattr(wspace,'import')(gen)
  getattr(wspace,'import')(gamgen)
  getattr(wspace,'import')(gamrecogen)
  data.Print("v")

  return wspace

def main():
  ws = createWorkspace()
  ws.Print()
  ws.writeToFile("JpsiWorkspace.root")

if __name__ == "__main__":
  test = main()
