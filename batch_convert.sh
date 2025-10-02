#!/usr/bin/env bash

#SBATCH -J "CZI to ZARR"
#SBATCH -A schwab
#SBATCH -t 30:00:00
#SBATCH --mem=32000
#SBATCH --mail-user=alexandra.zakieva@embl.de
#SBATCH --mail-type=FAIL,BEGIN,END


INDIR="/g/mobilelab/LiveConfocalSuperPlankton_DataPackage"
OUTDIR="/scratch/alex_zakieva/zarr"
eubi_cmd="/home/zakieva/miniforge3/envs/eubizarr/bin/eubi"

for path1 in "${INDIR}/"TREC_* ; do
	basepath1="$(basename $path1)"
	for path2 in "${INDIR}/${basepath1}/"LSM* ; do
		basepath2="$(basename $path2)"
		mkdir -p "${OUTDIR}/${basepath1}/${basepath2}"

		for filepath in "${INDIR}/${basepath1}/${basepath2}/"*.czi ; do
			for scene_index in {0..50}; do
				outname="${OUTDIR}/${basepath1}/${basepath2}/$(basename ${filepath%.*})_${scene_index}.ome.zarr"
				$eubi_cmd to_zarr \
					"$filepath" \
					"${outname}" \
					--includes PK2 \
					--scene_index ${scene_index} \
					--zarr_format 2
				echo "Completed processing ${filepath} scene index ${scene_index} to ${outname}"
			done
			echo "Completed processing file ${filepath}"
		done
	done
done
