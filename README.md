# Live Confocal Super Plankton

NOTA BENE
After the release of this accession, the community flagged key improvements that should be made. We will implement them in January 2026. Meanwhile, the most updated version of the OME-Zarr files are in the following S3 storage: https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets.
To open them in an OME-Zarr viewer, use the following naming convention:
- https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets/athens/'name'_tile'tile'.zarr
- https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets/barcelona/'name'_tile'tile'.zarr
- https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets/bilbao/'name'_tile'tile'.zarr
- https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets/kristineberg/'name'_tile'tile'.zarr
- https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets/naples/'name'_tile'tile'.zarr
- https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets/porto/'name'_tile'tile'.zarr
- https://s3.embl.de/live-confocal-trec-super-plankton/converted_datasets/tallinn/'name'_tile'tile'.zarr

where 'name' and 'tile' are the corresponding columns values in the BioImage Archive File List accession.

Supporting data processing and visualization scripts and documentation for the BioImage Archive submission

[TRaversing European Coastlines (TREC) Live Plankton High-Content Fluorescence Microscopy Dataset](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2258)

If you have any problem with accessing imaging data, please submit an issue. We will come back to you ASAP.

## Images visualisation on BioFile Finder (BFF)
1. Follow [this link](https://bff.allencell.org/app?c=File+Path%3A0.25%2Ctile%3A0.25%2Cname%3A0.25%2Cacquisition_date%3A0.25&source=%7B%22name%22%3A%22live_confocal_trec_super_plankton_BFF.csv+%2803%2F11%2F2025+15%3A59%3A26%29%22%2C%22type%22%3A%22csv%22%2C%22uri%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2FAlexandraZakieva%2Flive-confocal-super-plankton%2Frefs%2Fheads%2Fmain%2Flive_confocal_trec_super_plankton_BFF.csv%22%7D).
2. On the left panel, you can `Group by`, `Filter` or `Sort` the files at multiple levels. We recommend to group by `acquisition_location`, `acquisition_date` and `name`.
3. On the upper bar, you can adjust the view as list, big or small mosaic. BFF automatically generates thumbnails.
4. Select a file of your choice.
5. On the right panel, click on `OPEN FILE`.
6. Select `Vol-E` or `Neuroglancer`.
7. When opened in `Vol-E`, on the left panel, click on the third icon to display the OME-Zarr metadata.

## OME-XML metadata visualization
1. On BioFileFinder, find your image of interest and copy the corresponding S3 link.
2. Open a new browser page in Mozilla Firefox or Google Chrome.
3. Paste the S3 link into the web address field.
4. Append to the link "/OME/METADATA.ome.xml".
5. Press ENTER.

## BioImage Archive submission preparation workflow
1. Prior to image acquisition, samples were assigned with BioSamples IDs according to [BiOcean5D sampling Handbook](https://zenodo.org/records/11261905).
2. Primary data was organized in the following directory structure `<acquisition_location>/<acquisition_date>/<name>.czi`.
3. On [LabID](https://gitlab.com/lab-integrated-data), every file was mapped to BioSamples IDs, the Channel metadata was curated. The resulting [LabID Study](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/LabID_export.tsv) was exported.
4. [Eu-BI Bridge](https://euro-bioimaging.github.io/EuBI-Bridge) was used for converting primary data from CZI to OME-Zarr format in [batch](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/batch_convert.sh) using --scene_index option from 0 to 50. The data with acquisition_location "TREC_STOP_12_Tallinn" were also converted in [batch](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/batch_convert_Tallin.sh) using --mosaic_scene_index option from 0 to 60.
5. The OME-Zarr OME-XML and OMERO Channel metadata was then curated according to [LabID Study](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/LabID_export.tsv).
6. The curated OME-Zarr files were then copied to an S3 storage. Upon request, ChatGPT5 wrote a [command line](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/BFF_table_creation) to generate a BFF-compliant [table](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/live_confocal_trec_super_plankton_BFF.csv) listing all the OME-Zarr files on the S3 storage and adding helping columns.
7. The curated OME-Zarr files were zipped and submitted to [BioImage Archive](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2258).
8. Upon request, ChatGPT5 wrote a [JAVA Script](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/Metadata_from_CZI_to_TSV.js) to extract acquisition metadata from CZI files by using [Bio-Formats FIJI Plugin](https://github.com/ome/bioformats) and write them into TSV tables that were submitted to [BioImage Archive](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2258).
9. Upon request, ChatGPT5 wrote a [Python script](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/tsv_qc_filelist.py) to [quality check the conversion](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/Conversion_QC.tsv) at step 4 and generate a BioImage Archive-compliant File list. For this, [input_table_1](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/LabID_export.tsv) generated at the step 3 and [input_table_2](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/live_confocal_trec_super_plankton_BFF.csv) generated at the step 6 were used.
