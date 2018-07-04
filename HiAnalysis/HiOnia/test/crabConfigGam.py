from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'excGamGamMCRootupler16Jun18'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'hioniaproducer_pPb_80X_UPC_MC_cfg.py'

config.Data.inputDataset = '/gamgamMuMu_m4to8GeV/rrabadan-AODSIM-93f41661f8a748876475b063c76f7a3d/USER'
config.Data.inputDBS = 'phys03'
config.Data.splitting = 'FileBased' #FileBase
config.Data.unitsPerJob = 8

config.Data.outLFNDirBase = '/store/user/'+getUsernameFromSiteDB()+'/UPC8TeVMC/gamgamMuMuNoFilters'
config.Data.publication = False
config.Data.outputDatasetTag = 'Ntuples'
config.Data.ignoreLocality = False

config.Site.storageSite = 'T3_US_FNALLPC'
#config.Site.whitelist = ["T2_US*"]

