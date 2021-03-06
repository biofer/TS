/* Copyright (C) 2010 Ion Torrent Systems, Inc. All Rights Reserved */
#ifndef GLOBALWRITER_H
#define GLOBALWRITER_H

#include <stdio.h>
#include <sys/types.h>
#include "FlowBuffer.h"
#include "Mask.h"
#include "Region.h"
#include "RegionTracker.h"
#include "BeadParams.h"
#include "BeadTracker.h"

class BkgTrace;

class BkgDataPointers; // forward declaration to avoid including <armadillo> which is in BkgDataPointers.h
class PinnedInFlow;
class TimeCompression;
class EmphasisClass;
class RegionalizedData;
class SlicedChipExtras;

// things referred to globally
class GlobalWriter
{
  // the actual output of this whole process
  class RawWells    *rawWells;

public:
  // mask that indicate where beads/pinned wells are located
  // shared across threads, but pinning is only up to flow 0
  Mask        *bfmask;  // global information on bead type and layout
  int16_t *washout_flow;
  // array to keep track of flows for which empty wells are unpinned
  // shared across threads
  const PinnedInFlow *pinnedInFlow;  // not regional, set when creating this object

  // name our output directory
  std::string dirName;

  BkgDataPointers *mPtrs;

  GlobalWriter();

  // We keep local copies of these exterior pointers.
  void FillExternalLinks(Mask *_bfmask, const PinnedInFlow *_pinnedInFlow, 
                         class RawWells *_rawWells, int16_t *_washout_flow);
  void SetHdf5Pointer(BkgDataPointers *_my_hdf5);
  void MakeDirName(const char *_results_folder);
  void DeLink();

  void WriteBeadParameterstoDataCubes (int iFlowBuffer, bool last, Region *region, BeadTracker &my_beads, FlowBufferInfo &my_flow, BkgTrace &my_trace, int flow_block_id, int flow_block_start);
  void WriteOneBeadToDataCubes(BeadParams &p, int flow, int iFlowBuffer, int last, int ibd, Region *region, BkgTrace &my_trace, int flow_block_size, int flow_block_id);
  void WriteRegionParametersToDataCubes(RegionalizedData *my_region_data, 
    SlicedChipExtras *my_region_data_extras, 
    int max_frames, int flow_block_size, int flow_block_id, int flow_block_start,
    bool last, int last_flow );
  
  ~GlobalWriter();
  void DumpTimeCompressionH5 ( int reg, TimeCompression &time_c, int max_frames );
  void DumpRegionFitParamsH5 (int region_ndx, int flow, reg_params &rp, int flow_block_size, int flow_block_id );
  void DumpRegionOffsetH5(int reg, int col, int row );
  void DumpEmptyTraceH5 ( int reg, RegionalizedData &my_region_data, 
                          SlicedChipExtras *my_region_data_extras, int flow_block_start,
                          bool last, int last_flow );
  void DumpRegionInitH5 (int reg, RegionalizedData &my_region_data);
  void DumpDarknessH5(int reg, reg_params &my_rp, int flow_block_size );
  void DumpDarkMatterH5(int reg, TimeCompression &time_c, RegionTracker &my_reg_tracker, int max_frames);
  void DumpTimeAndEmphasisByRegionH5 (int reg, TimeCompression &time_c, EmphasisClass &emphasis_data, int max_frames);
  void SendErrorVectorToHDF5 (BeadParams *p, error_track &err_t, Region *region, FlowBufferInfo &my_flow, int flow_block_start);
  void SendPredictedToHDF5 (int ibd, float *block_signal_predicted, RegionalizedData &my_region_data, SlicedChipExtras &my_region_data_extras, int max_frames, int flow_block_start);
  void SendCorrectedToHDF5 (int ibd, float *block_signal_corrected, RegionalizedData &my_region_data, SlicedChipExtras &my_region_data_extras, int max_frames, int flow_block_start);
  void SendXtalkToHDF5 (int ibd, float *block_signal_xtalk, RegionalizedData &my_region_data, SlicedChipExtras &my_region_data_extras, int max_frames, int flow_block_start );
  void WriteDebugBeadToRegionH5 ( RegionalizedData *my_region_data, 
                                  SlicedChipExtras *my_region_data_extras,
                                  int flow_block_start, bool last, int last_flow );
  void WriteAnswersToWells (int iFlowBuffer, Region *region, RegionTracker *my_regions, BeadTracker &my_beads, int flow_block_start );
  void DumpRegionNucShape( reg_params &rp, int region_ndx, int iBlk, int &i_param, int flow_block_size);
  void DumpRegionalBuffering( reg_params &rp, int region_ndx, int iBlk, int &i_param);
  void DumpRegionalEnzymatics( reg_params &rp, int region_ndx, int iBlk,int  &i_param);
  void SpecificRegionParamDump ( reg_params &rp, int region_ndx, int iBlk, int flow_block_size);
  // bestRegion
  void SendBestRegion_LocationToHDF5 (int ibd, RegionalizedData &my_region_data );
  void SendBestRegion_PredictedToHDF5 (int ibd, float *block_signal_predicted, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames, int flow_block_start);
  void SendBestRegion_CorrectedToHDF5 (int ibd, float *block_signal_corrected, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames, int flow_block_start);
  void SendBestRegion_AmplitudeToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendBestRegion_ResidualToHDF5 (int ibd, error_track &err_t, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendBestRegion_KmultToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendBestRegion_DmultToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendBestRegion_SPToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendBestRegion_RToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendBestRegion_FitType_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int fitType[], int flow_block_start );
  void SendBestRegion_GainSensToHDF5 (int ibd, RegionalizedData &my_region_data );
  void SendBestRegion_TimeframeToHDF5 (RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames);
  // xyflow
  int select_xy(int x, int y);
  int select_xyflow(int x, int y, int flow);
  int mm_xyflow(int x, int y, int flow);
  std::string hp_xyflow(int x, int y, int flow);
  void SendXyflow_Predicted_ToHDF5 (int ibd, float *block_signal_predicted, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames, int flow_block_start );
  void SendXyflow_Corrected_ToHDF5 (int ibd, float *block_signal_corrected, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames, int flow_block_start );
  void SendXyflow_Amplitude_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_Residual_ToHDF5 (int ibd, error_track &err_t, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_Location_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_HPlen_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras &extra, int flow_block_start );
  void SendXyflow_FitType_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras , int fitType[], int flow_block_start );
  void SendXyflow_Kmult_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_Dmult_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_MM_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_SP_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_R_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int flow_block_start );
  void SendXyflow_Timeframe_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames, int flow_block_start );
  // keys (TCAG) corresponding to xyflow
  void SendXyflow_Location_Keys_ToHDF5 (int ibd, RegionalizedData &my_region_data, SlicedChipExtras &my_region_data_extras, int flow_block_start );
  void SendXyflow_Predicted_Keys_ToHDF5 (int ibd, float *block_signal_predicted, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames, int flow_block_start );
  void SendXyflow_Corrected_Keys_ToHDF5 (int ibd, float *block_signal_corrected, RegionalizedData &my_region_data, SlicedChipExtras & my_region_data_extras, int max_frames, int flow_block_start );

 private:

  // Serialization section
  friend class boost::serialization::access;
  template<typename Archive>
    void save(Archive& ar, const unsigned version) const {
      ar &
	bfmask &
	pinnedInFlow &
	// rawWells &
	// mPtrs &    // ??
	dirName;
      fprintf(stdout, "Serialization in GlobalWriter: need to rebuild rawWells, mPtrs\n");
  }
  template<typename Archive>
    void load(Archive& ar, const unsigned version) {
      ar &
	bfmask &
	pinnedInFlow &
	// rawWells & // ??
	// mPtrs &    // ??
	dirName;
  }
  BOOST_SERIALIZATION_SPLIT_MEMBER()

};



#endif // GLOBALWRITER_H
