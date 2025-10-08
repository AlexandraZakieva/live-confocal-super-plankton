# Live Confocal Super Plankton
Supporting data processing and visualization scripts and documentation for the BioImage Archive submission

[TRaversing European Coastlines (TREC) Live Plankton High-Content Fluorescence Microscopy Dataset](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2258)

If you have any problem with accessing imaging data, please submit an issue. We will come back to you ASAP.

## OME-Zarr visualisation on BioFile Finder (BFF)
1. Download [this table](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/live_confocal_trec_super_plankton_BFF.csv).
2. Go to https://bff.allencell.org.
3. Click on `GET STARTED`.
4. Click on `CHOOSE FILE`.
5. Select the file downloaded at the step 1.
6. Click on `LOAD`.
7. On the left panel, you can `Group by`, `Filter` or `Sort` the files at multiple levels.
8. On the upper bar, you can adjust the view. BFF automatically generates thumbnails.
9. Select a file of your choice.
10. On the right panel, click on `OPEN FILE`.
11. Select `Vol-E`.
12. On the left panel, click on the third icon to display the OME-Zarr metadata.

## OME-XML metadata visualization
1. On BioFileFinder, find your image of interest and copy the corresponding S3 link.
2. Open a new browser page.
3. Paste the S3 link to the web address field.
4. Append to the link "/OME/METADATA.ome.xml".
5. Press ENTER.

## BioImage Archive submission preparation workflow
1. Prior to image acquisition, samples were assigned with BioSamples IDs according to [BiOcean5D sampling Handbook](https://zenodo.org/records/11261905).
2. Primary data was organized in the following directory structure `<acquisition_location>/<acquisition_date>/<name>.czi`.
3. On [LabID](https://gitlab.com/lab-integrated-data), every file was mapped to BioSamples IDs, the Channel metadata was curated. The resulting [LabID Study](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/LabID_export.tsv) was exported.
4. [Eu-BI Bridge](https://euro-bioimaging.github.io/EuBI-Bridge) was used for converting primary data from CZI to OME-Zarr format in [batch](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/batch_convert.sh).
5. The OME-Zarr OME-XML and OMERO Channel metadata was then curated according to [LabID Study](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/LabID_export.tsv).
6. The curated OME-Zarr files were then copied to an S3 storage. Upon request, ChatGPT5 wrote a [command line](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/BFF_table_creation) to generate a BFF-compliant [table](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/live_confocal_trec_super_plankton_BFF.csv) listing all the OME-Zarr files on the S3 storage and adding helping columns.
7. The curated OME-Zarr files were zipped and submitted to [BioImage Archive](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2258).
8. Upon request, ChatGPT5 wrote a [JAVA Script](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/Metadata_from_CZI_to_TSV.js) to extract acquisition metadata from CZI files by using [Bio-Formats FIJI Plugin](https://github.com/ome/bioformats) and write them into TSV tables that were submitted to [BioImage Archive](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2258).
9. Upon request, ChatGPT5 wrote a [Python script](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/tsv_qc_filelist.py) to [quality check the conversion](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/Conversion_QC.tsv) at step 4 and generate a BioImage Archive-compliant File list. For this, [input_table_1](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/LabID_export.tsv) generated at the step 3 and [input_table_2](https://github.com/AlexandraZakieva/live-confocal-super-plankton/blob/main/live_confocal_trec_super_plankton_BFF.csv) generated at the step 6 were used.
