import FWCore.ParameterSet.Config as cms

from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.jetTools import *
from PhysicsTools.PatAlgos.tools.tauTools import *

from PhysicsTools.PatAlgos.tools.helpers import listModules, applyPostfix, getPatAlgosToolsTask, addToProcessAndTask

from copy import deepcopy

def warningIsolation():
    print("WARNING: particle based isolation must be studied")

def adaptPFMuons(process,module,postfix="", muonMatchModule=None ):
    print("Adapting PF Muons ")
    print("***************** ")
    #warningIsolation()
    print()
    module.useParticleFlow = True
    module.pfMuonSource    = cms.InputTag("pfIsolatedMuonsPFBRECO" + postfix)
    module.userIsolation   = cms.PSet()
    ## module.isoDeposits = cms.PSet(
    ##     pfChargedHadrons = cms.InputTag("muPFIsoDepositCharged" + postfix),
    ##     pfChargedAll = cms.InputTag("muPFIsoDepositChargedAll" + postfix),
    ##     pfPUChargedHadrons = cms.InputTag("muPFIsoDepositPU" + postfix),
    ##     pfNeutralHadrons = cms.InputTag("muPFIsoDepositNeutral" + postfix),
    ##     pfPhotons = cms.InputTag("muPFIsoDepositGamma" + postfix)
    ##     )
    ## module.isolationValues = cms.PSet(
    ##     pfChargedHadrons = cms.InputTag("muPFIsoValueCharged04"+ postfix),
    ##     pfChargedAll = cms.InputTag("muPFIsoValueChargedAll04"+ postfix),
    ##     pfPUChargedHadrons = cms.InputTag("muPFIsoValuePU04" + postfix),
    ##     pfNeutralHadrons = cms.InputTag("muPFIsoValueNeutral04" + postfix),
    ##     pfPhotons = cms.InputTag("muPFIsoValueGamma04" + postfix)
    ##     )
    # matching the pfMuons, not the standard muons.
    if muonMatchModule == None :
        applyPostfix(process,"muonMatch",postfix).src = module.pfMuonSource
    else :
        muonMatchModule.src = module.pfMuonSource

    print(" muon source:", module.pfMuonSource)
    ## print " isolation  :",
    ## print module.isolationValues
    ## print " isodeposits: "
    ## print module.isoDeposits
    print()


def adaptPFElectrons(process,module, postfix):
    # module.useParticleFlow = True
    print("Adapting PF Electrons ")
    print("********************* ")
    #warningIsolation()
    print()
    module.useParticleFlow = True
    module.pfElectronSource = cms.InputTag("pfIsolatedElectronsPFBRECO" + postfix)
    module.userIsolation   = cms.PSet()
    ## module.isoDeposits = cms.PSet(
    ##     pfChargedHadrons = cms.InputTag("elPFIsoDepositCharged" + postfix),
    ##     pfChargedAll = cms.InputTag("elPFIsoDepositChargedAll" + postfix),
    ##     pfPUChargedHadrons = cms.InputTag("elPFIsoDepositPU" + postfix),
    ##     pfNeutralHadrons = cms.InputTag("elPFIsoDepositNeutral" + postfix),
    ##     pfPhotons = cms.InputTag("elPFIsoDepositGamma" + postfix)
    ##     )
    ## module.isolationValues = cms.PSet(
    ##     pfChargedHadrons = cms.InputTag("elPFIsoValueCharged04PFId"+ postfix),
    ##     pfChargedAll = cms.InputTag("elPFIsoValueChargedAll04PFId"+ postfix),
    ##     pfPUChargedHadrons = cms.InputTag("elPFIsoValuePU04PFId" + postfix),
    ##     pfNeutralHadrons = cms.InputTag("elPFIsoValueNeutral04PFId" + postfix),
    ##     pfPhotons = cms.InputTag("elPFIsoValueGamma04PFId" + postfix)
    ##     )

    # COLIN: since we take the egamma momentum for pat Electrons, we must
    # match the egamma electron to the gen electrons, and not the PFElectron.
    # -> do not uncomment the line below.
    # process.electronMatch.src = module.pfElectronSource
    # COLIN: how do we depend on this matching choice?

    print(" PF electron source:", module.pfElectronSource)
    ## print " isolation  :"
    ## print module.isolationValues
    ## print " isodeposits: "
    ## print module.isoDeposits
    print()




def adaptPFPhotons(process,module):
    raise RuntimeError("Photons are not supported yet")

from RecoTauTag.RecoTau.TauDiscriminatorTools import adaptTauDiscriminator, producerIsTauTypeMapper

def reconfigurePF2PATTaus(process,
      tauType='shrinkingConePFTau',
      pf2patSelection=["DiscriminationByIsolation", "DiscriminationByLeadingPionPtCut"],
      selectionDependsOn=["DiscriminationByLeadingTrackFinding"],
      producerFromType=lambda producer: producer+"Producer",
      postfix = ""):
    print("patTaus will be produced from taus of type: %s that pass %s" \
          % (tauType, pf2patSelection))



    # Get the prototype of tau producer to make, i.e. fixedConePFTauProducer
    producerName = producerFromType(tauType)
    # Set as the source for the pf2pat taus (pfTaus) selector
    applyPostfix(process,"pfTaus", postfix).src = producerName+postfix
    # Start our pf2pat taus base sequence
    oldTauSansRefs = getattr(process,'pfTausProducerSansRefs'+postfix)
    oldTau = getattr(process,'pfTausProducer'+postfix)
    ## copy tau and setup it properly
    newTauSansRefs = None
    newTau = getattr(process,producerName+postfix).clone()

    ## adapted to new structure in RecoTauProducers PLEASE CHECK!!!
    if tauType=='shrinkingConePFTau':
        newTauSansRefs = getattr(process,producerName+"SansRefs").clone()
        newTauSansRefs.modifiers[1] = cms.PSet(
            pfTauTagInfoSrc = cms.InputTag("pfTauTagInfoProducer"+postfix),
            name = cms.string('pfTauTTIworkaround'+postfix),
            plugin = cms.string('RecoTauTagInfoWorkaroundModifer')
            )
        newTau.modifiers[1] = newTauSansRefs.modifiers[1]
        newTauSansRefs.piZeroSrc = "pfJetsLegacyTaNCPiZeros"+postfix
        newTau.piZeroSrc = newTauSansRefs.piZeroSrc
        newTauSansRefs.builders[0].pfCandSrc = oldTauSansRefs.builders[0].pfCandSrc
        newTauSansRefs.jetRegionSrc = oldTauSansRefs.jetRegionSrc
        newTauSansRefs.jetSrc = oldTauSansRefs.jetSrc
    elif tauType=='fixedConePFTau':
        newTau.piZeroSrc = "pfJetsLegacyTaNCPiZeros"+postfix
    elif tauType=='hpsPFTau':
        newTau = getattr(process,'combinatoricRecoTaus'+postfix).clone()
        newTau.piZeroSrc="pfJetsLegacyHPSPiZeros"+postfix
        newTau.modifiers[3] = cms.PSet(
            pfTauTagInfoSrc = cms.InputTag("pfTauTagInfoProducer"+postfix),
            name = cms.string('pfTauTTIworkaround'+postfix),
            plugin = cms.string('RecoTauTagInfoWorkaroundModifer')
            )
        from PhysicsTools.PatAlgos.tools.helpers import cloneProcessingSnippet
        #cloneProcessingSnippet(process, process.produceHPSPFTaus, postfix, addToTask = True)
        setattr(process,'produceHPSPFTaus'+postfix,cms.Sequence(applyPostfix(process,'hpsSelectionDiscriminator',postfix)+applyPostfix(process,'hpsPFTauProducerSansRefs',postfix)+applyPostfix(process,'hpsPFTauProducer',postfix)))
        massSearchReplaceParam(getattr(process,"produceHPSPFTaus"+postfix),
                               "PFTauProducer",
                               cms.InputTag("combinatoricRecoTaus"+postfix),
                               cms.InputTag("pfTausBase"+postfix) )
        massSearchReplaceParam(getattr(process,"produceHPSPFTaus"+postfix),
                               "src",
                               cms.InputTag("combinatoricRecoTaus"+postfix),
                               cms.InputTag("pfTausBase"+postfix) )
    ### Next three lines crash, oldTau does not have any of these attributes. Why?###
    #newTau.builders[0].pfCandSrc = oldTau.builders[0].pfCandSrc
    #newTau.jetRegionSrc = oldTau.jetRegionSrc
    #newTau.jetSrc = oldTau.jetSrc
    #newTau.builders[0].pfCandSrc = cms.InputTag("pfNoElectronJME" + postfix)
    #newTau.jetRegionSrc = cms.InputTag("pfTauPFJets08Region" + postfix)
    #newTau.jetSrc = cms.InputTag("pfJetsPFBRECO" + postfix)
    # replace old tau producer by new one put it into baseSequence
    task = getPatAlgosToolsTask(process)
    addToProcessAndTask("pfTausBase"+postfix, newTau, process, task)
    if tauType=='shrinkingConePFTau':
        addToProcessAndTask("pfTausBaseSansRefs"+postfix, newTauSansRefs, process, task)
        getattr(process,"pfTausBase"+postfix).src = "pfTausBaseSansRefs"+postfix
        baseSequence += getattr(process,"pfTausBaseSansRefs"+postfix)

    #make custom mapper to take postfix into account (could have gone with lambda of lambda but... )
    def producerIsTauTypeMapperWithPostfix(tauProducer):
        return lambda x: producerIsTauTypeMapper(tauProducer)+x.group(1)+postfix

    def recoTauTypeMapperWithGroup(tauProducer):
        return "%s(.*)"%recoTauTypeMapper(tauProducer)

    # Get our prediscriminants
    for predisc in selectionDependsOn:
        # Get the prototype
        originalName = tauType+predisc # i.e. fixedConePFTauProducerDiscriminationByLeadingTrackFinding
        clonedName = "pfTausBase"+predisc+postfix
        clonedDisc = getattr(process, originalName).clone()
        addToProcessAndTask(clonedName, clonedDisc, process, task)

        tauCollectionToSelect = None
        if tauType != 'hpsPFTau' :
            tauCollectionToSelect = "pfTausBase"+postfix
            #cms.InputTag(clonedDisc.PFTauProducer.value()+postfix)
        else:
            tauCollectionToSelect = "hpsPFTauProducer"+postfix
        # Adapt this discriminator for the cloned prediscriminators
        adaptTauDiscriminator(clonedDisc, newTauProducer="pfTausBase",
                              oldTauTypeMapper=recoTauTypeMapperWithGroup,
                              newTauTypeMapper=producerIsTauTypeMapperWithPostfix,
                              preservePFTauProducer=True)
        clonedDisc.PFTauProducer = tauCollectionToSelect

    # Reconfigure the pf2pat PFTau selector discrimination sources
    getattr(process,"pfTaus" + postfix).discriminators = cms.VPSet()
    for selection in pf2patSelection:
        # Get our discriminator that will be used to select pfTaus
        originalName = tauType+selection
        clonedName = "pfTausBase"+selection+postfix
        clonedDisc = getattr(process, originalName).clone()
        addToProcessAndTask(clonedName, clonedDisc, process, task)

        tauCollectionToSelect = None

        if tauType != 'hpsPFTau' :
            tauCollectionToSelect = cms.InputTag("pfTausBase"+postfix)
            #cms.InputTag(clonedDisc.PFTauProducer.value()+postfix)
        else:
            tauCollectionToSelect = cms.InputTag("hpsPFTauProducer"+postfix)
        #Adapt our cloned discriminator to the new prediscriminants
        adaptTauDiscriminator(clonedDisc, newTauProducer="pfTausBase",
                              oldTauTypeMapper=recoTauTypeMapperWithGroup,
                              newTauTypeMapper=producerIsTauTypeMapperWithPostfix,
                              preservePFTauProducer=True)
        clonedDisc.PFTauProducer = tauCollectionToSelect

        # Add this selection to our pfTau selectors
        getattr(process,"pfTaus" + postfix).discriminators.append(cms.PSet(
           discriminator=cms.InputTag(clonedName), selectionCut=cms.double(0.5)))
        # Set the input of the final selector.
        if tauType != 'hpsPFTau':
            getattr(process,"pfTaus" + postfix).src = "pfTausBase"+postfix
        else:
            # If we are using HPS taus, we need to take the output of the clenaed
            # collection
            getattr(process,"pfTaus" + postfix).src = "hpsPFTauProducer"+postfix



def adaptPFTaus(process,tauType = 'shrinkingConePFTau', postfix = ""):
    # Set up the collection used as a preselection to use this tau type
    if tauType != 'hpsPFTau' :
        reconfigurePF2PATTaus(process, tauType, postfix=postfix)
    else:
        reconfigurePF2PATTaus(process, tauType,
                              ["DiscriminationByDecayModeFinding"],
                              ["DiscriminationByDecayModeFinding"],
                              postfix=postfix)
    # new default use unselected taus (selected only for jet cleaning)
    if tauType != 'hpsPFTau' :
        getattr(process,"patTaus" + postfix).tauSource = cms.InputTag("pfTausBase"+postfix)
    else:
        getattr(process,"patTaus" + postfix).tauSource = cms.InputTag("hpsPFTauProducer"+postfix)
    # to use preselected collection (old default) uncomment line below
    #applyPostfix(process,"patTaus", postfix).tauSource = cms.InputTag("pfTaus"+postfix)

        ### apparently not needed anymore, function gone from tauTools.py###
    #redoPFTauDiscriminators(process,
                            #cms.InputTag(tauType+'Producer'),
                            #applyPostfix(process,"patTaus", postfix).tauSource,
                            #tauType, postfix=postfix)


    if tauType != 'hpsPFTau' :
        switchToPFTauByType(process, pfTauType=tauType,
                                patTauLabel="pfTausBase"+postfix,
                                tauSource=cms.InputTag(tauType+'Producer'+postfix),
                                postfix=postfix)
        getattr(process,"patTaus" + postfix).tauSource = cms.InputTag("pfTausBase"+postfix)
    else:
        switchToPFTauByType(process, pfTauType=tauType,
                                patTauLabel="",
                                tauSource=cms.InputTag(tauType+'Producer'+postfix),
                                postfix=postfix)
        getattr(process,"patTaus" + postfix).tauSource = cms.InputTag("hpsPFTauProducer"+postfix)



#helper function for PAT on PF2PAT sample
def tauTypeInPF2PAT(process,tauType='shrinkingConePFTau', postfix = ""):
    process.load("CommonTools.ParticleFlow.pfTaus_cff")
    applyPostfix(process, "pfTaus",postfix).src = cms.InputTag(tauType+'Producer'+postfix)


def addPFCandidates(process,src,patLabel='PFParticles',cut="",postfix=""):
    from PhysicsTools.PatAlgos.producersLayer1.pfParticleProducer_cfi import patPFParticles
    # make modules
    producer = patPFParticles.clone(pfCandidateSource = src)
    filter   = cms.EDFilter("PATPFParticleSelector",
                    src = cms.InputTag("pat" + patLabel),
                    cut = cms.string(cut))
    counter  = cms.EDFilter("PATCandViewCountFilter",
                    minNumber = cms.uint32(0),
                    maxNumber = cms.uint32(999999),
                    src       = cms.InputTag("pat" + patLabel))
    # add modules to process
    task = getPatAlgosToolsTask(process)
    addToProcessAndTask("pat" + patLabel, producer, process, task)
    addToProcessAndTask("selectedPat" + patLabel, filter, process, task)
    addToProcessAndTask("countPat" + patLabel, counter, process, task)

    # summary tables
    applyPostfix(process, "patCandidateSummary", postfix).candidates.append(cms.InputTag('pat' + patLabel))
    applyPostfix(process, "selectedPatCandidateSummary", postfix).candidates.append(cms.InputTag('selectedPat' + patLabel))


def switchToPFMET(process,input=cms.InputTag('pfMETPFBRECO'), type1=False, postfix=""):
    print('MET: using ', input)
    if( not type1 ):
        oldMETSource = applyPostfix(process, "patMETs",postfix).metSource
        applyPostfix(process, "patMETs",postfix).metSource = input
        applyPostfix(process, "patMETs",postfix).addMuonCorrections = False
    else:
        # type1 corrected MET
        # name of corrected MET hardcoded in PAT and meaningless
        print('Apply TypeI corrections for MET')
        #getattr(process, "patPF2PATSequence"+postfix).remove(applyPostfix(process, "patMETCorrections",postfix))
        jecLabel = getattr(process,'patJetCorrFactors'+postfix).payload.pythonValue().replace("'","")
        getattr(process,jecLabel+'Type1CorMet'+postfix).src = input.getModuleLabel()
        #getattr(process,'patMETs'+postfix).metSource = jecLabel+'Type1CorMet'+postfix
        #getattr(process,'patMETs'+postfix).addMuonCorrections = False

def switchToPFJets(process, input=cms.InputTag('pfNoTauClones'), algo='AK4', postfix = "", jetCorrections=('AK4PFchs', ['L1FastJet','L2Relative', 'L3Absolute']), type1=False, outputModules=['out']):

    print("Switching to PFJets,  ", algo)
    print("************************ ")
    print("input collection: ", input)

    if algo == 'AK4':
        genJetCollection = cms.InputTag('ak4GenJetsNoNu'+postfix)
        rParam=0.4
    elif algo == 'AK7':
        genJetCollection = cms.InputTag('ak7GenJetsNoNu'+postfix)
        rParam=0.7
    else:
        print('bad jet algorithm:', algo, '! for now, only AK4 and AK7 are allowed. If you need other algorithms, please contact Colin')
        sys.exit(1)

    # changing the jet collection in PF2PAT:
    from CommonTools.ParticleFlow.Tools.jetTools import jetAlgo
    inputCollection = getattr(process,"pfJetsPFBRECO"+postfix).src
    setattr(process,"pfJetsPFBRECO"+postfix,jetAlgo(algo)) # problem for cfgBrowser
    getattr(process,"pfJetsPFBRECO"+postfix).src = inputCollection
    inputJetCorrLabel=jetCorrections

    switchJetCollection(process,
                        jetSource = input,
                        algo=algo,
                        rParam=rParam,
                        genJetCollection=genJetCollection,
                        postfix=postfix,
                        jetTrackAssociation=True,
                        jetCorrections=inputJetCorrLabel,
                        outputModules = outputModules,
                        )

    # check whether L1FastJet is in the list of correction levels or not
    applyPostfix(process, "patJetCorrFactors", postfix).useRho = False
    task = getPatAlgosToolsTask(process)
    for corr in inputJetCorrLabel[1]:
        if corr == 'L1FastJet':
            applyPostfix(process, "patJetCorrFactors", postfix).useRho = True
            applyPostfix(process, "pfJetsPFBRECO", postfix).doAreaFastjet = True
            # do correct treatment for TypeI MET corrections
            #type1=True
            if type1:
                for mod in process.producerNames().split(' '):

                    if mod.startswith("kt6") and mod.endswith("Jets"+postfix) and not 'GenJets' in mod:
                        prefix = mod.replace(postfix,'')
                        prefix = prefix.replace('kt6PFJets','')
                        prefix = prefix.replace('kt6CaloJets','')
                        prefix = getattr(process,'patJetCorrFactors'+prefix+postfix).payload.pythonValue().replace("'","")
                        for essource in process.es_sources_().keys():
                            if essource == prefix+'L1FastJet':
                                setattr(process,essource+postfix,getattr(process,essource).clone(srcRho=cms.InputTag(mod,'rho')))
                                addToProcessAndTask(prefix+'CombinedCorrector'+postfix,
                                                    getattr(process,prefix+'CombinedCorrector').clone(), process, task)
                                getattr(process,prefix+'CorMet'+postfix).corrector = prefix+'CombinedCorrector'+postfix
                                for cor in getattr(process,prefix+'CombinedCorrector'+postfix).correctors:
                                    if cor == essource:
                                        idx = getattr(process,prefix+'CombinedCorrector'+postfix).correctors.index(essource);
                                        getattr(process,prefix+'CombinedCorrector'+postfix).correctors[idx] = essource+postfix

    if hasattr( getattr( process, "patJets" + postfix), 'embedCaloTowers' ): # optional parameter, which defaults to 'False' anyway
        applyPostfix(process, "patJets", postfix).embedCaloTowers = False
    applyPostfix(process, "patJets", postfix).embedPFCandidates = True

#-- Remove MC dependence ------------------------------------------------------
def removeMCMatchingPF2PAT( process, postfix="", outputModules=['out'] ):
    #from PhysicsTools.PatAlgos.tools.coreTools import removeMCMatching
    ### no longe needed in unscheduled mode###
    #removeIfInSequence(process, "genForPF2PATSequence", "patDefaultSequence", postfix)
    removeMCMatching(process, names=['All'], postfix=postfix, outputModules=outputModules)


def adaptPVs(process, pvCollection=cms.InputTag('offlinePrimaryVertices'), postfix=''):
    print("Switching PV collection for PF2PAT:", pvCollection)
    print("***********************************")

    # PV sources to be exchanged:
    pvExchange = ['Vertices','vertices','pvSrc','primaryVertices','srcPVs','primaryVertex']
    # PV sources NOT to be exchanged:
    #noPvExchange = ['src','PVProducer','primaryVertexSrc','vertexSrc']

    # exchange the primary vertex source of all relevant modules
    for m in (process.producerNames().split(' ') + process.filterNames().split(' ')):
        # only if the module has a source with a relevant name
        for namePvSrc in pvExchange:
            if hasattr(getattr(process,m),namePvSrc):
                #print m
                setattr(getattr(process,m),namePvSrc,deepcopy(pvCollection))


def usePF2PAT(process,runPF2PAT=True, jetAlgo='AK4', runOnMC=True, postfix="", jetCorrections=('AK4PFchs', ['L1FastJet','L2Relative','L3Absolute'],'None'), pvCollection=cms.InputTag('goodOfflinePrimaryVerticesPFlow',), typeIMetCorrections=False, outputModules=['out'],excludeFromTopProjection=['Tau']):
    # PLEASE DO NOT CLOBBER THIS FUNCTION WITH CODE SPECIFIC TO A GIVEN PHYSICS OBJECT.
    # CREATE ADDITIONAL FUNCTIONS IF NEEDED.

    if typeIMetCorrections:
        jetCorrections = (jetCorrections[0],jetCorrections[1],'Type-1')
    """Switch PAT to use PF2PAT instead of AOD sources. if 'runPF2PAT' is true, we'll also add PF2PAT in front of the PAT sequence"""

    # -------- CORE ---------------
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix
    patAlgosToolsTask = getPatAlgosToolsTask(process)
    taskLabel = patAlgosToolsTask.label()
    if runPF2PAT:
        loadWithPostfix(process,'PhysicsTools.PatAlgos.patSequences_cff',postfix, loadedProducersAndFilters=taskLabel)
        loadWithPostfix(process,"CommonTools.ParticleFlow.PFBRECO_cff",postfix, loadedProducersAndFilters=taskLabel)
    else:
        loadWithPostfix(process,'PhysicsTools.PatAlgos.patSequences_cff',postfix, loadedProducersAndFilters=taskLabel)




    # -------- OBJECTS ------------
    # Muons

    adaptPFMuons(process,
                 applyPostfix(process,"patMuons",postfix),
                 postfix)

    # Electrons

    adaptPFElectrons(process,
                     applyPostfix(process,"patElectrons",postfix),
                     postfix)

    # Photons
    #print "Temporarily switching off photons completely"

    #removeSpecificPATObjects(process,names=['Photons'],outputModules=outputModules,postfix=postfix)

    # Jets
    if runOnMC :
        switchToPFJets( process, cms.InputTag('pfNoTauClonesPFBRECO'+postfix), jetAlgo, postfix=postfix,
                        jetCorrections=jetCorrections, type1=typeIMetCorrections, outputModules=outputModules )

    else :
        if not 'L2L3Residual' in jetCorrections[1]:
                ### think of a more accurate warning
            print('#################################################')
            print('WARNING! Not using L2L3Residual but this is data.')
            print('If this is okay with you, disregard this message.')
            print('#################################################')
        switchToPFJets( process, cms.InputTag('pfNoTauClonesPFBRECO'+postfix), jetAlgo, postfix=postfix,
                        jetCorrections=jetCorrections, type1=typeIMetCorrections, outputModules=outputModules )
    # Taus
    #adaptPFTaus( process, tauType='shrinkingConePFTau', postfix=postfix )
    #adaptPFTaus( process, tauType='fixedConePFTau', postfix=postfix )
    adaptPFTaus( process, tauType='hpsPFTau', postfix=postfix )
    # MET
    switchToPFMET(process, cms.InputTag('pfMETPFBRECO'+postfix), type1=typeIMetCorrections, postfix=postfix)

    # Unmasked PFCandidates
    addPFCandidates(process,cms.InputTag('pfNoJetClones'+postfix),patLabel='PFParticles'+postfix,cut="",postfix=postfix)

    # adapt primary vertex collection
    adaptPVs(process, pvCollection=pvCollection, postfix=postfix)

    if not runOnMC:
        runOnData(process,postfix=postfix,outputModules=outputModules)

    # Configure Top Projections
    getattr(process,"pfNoPileUpJME"+postfix).enable = True
    getattr(process,"pfNoMuonJMEPFBRECO"+postfix).enable = True
    getattr(process,"pfNoElectronJMEPFBRECO"+postfix).enable = True
    getattr(process,"pfNoTauPFBRECO"+postfix).enable = False
    getattr(process,"pfNoJetPFBRECO"+postfix).enable = True
    exclusionList = ''
    for object in excludeFromTopProjection:
        jme = ''
        if object in ['Muon','Electron']:
            jme = 'JME'
        getattr(process,"pfNo"+object+jme+'PFBRECO'+postfix).enable = False
        exclusionList=exclusionList+object+','
    exclusionList=exclusionList.rstrip(',')
    print("Done: PFBRECO interfaced to PAT, postfix=", postfix,", Excluded from Top Projection:",exclusionList)
