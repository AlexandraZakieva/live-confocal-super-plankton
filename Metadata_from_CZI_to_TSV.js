// Fiji Script — Language: JavaScript (Nashorn)
// Export ORIGINAL CZI metadata to TSV, skipping XML-like values only.
// Output goes to a flat directory "<output>/CZI_metadata" with filenames "<base>.tsv".
// If filenames collide, "_1", "_2", ... are appended automatically.
//
// Requires Bio-Formats (bundled with Fiji).

importClass(Packages.ij.IJ);
importClass(Packages.java.io.File);
importClass(Packages.java.io.FileOutputStream);
importClass(Packages.java.io.OutputStreamWriter);
importClass(Packages.java.io.BufferedWriter);
importClass(Packages.java.nio.charset.StandardCharsets);

// Bio-Formats (use CZI reader to keep original metadata)
importClass(Packages.loci.formats.in.ZeissCZIReader);
importClass(Packages.loci.common.DebugTools);

(function main() {
  // Keep logs quiet; we’re not generating OME metadata
  try { DebugTools.setRootLevel("ERROR"); } catch (e) {}

  var inRoot  = IJ.getDirectory("Choose input_directory (root with CZI files)");
  if (inRoot == null) { IJ.showMessage("Cancelled","No input directory selected."); return; }
  var outRoot = IJ.getDirectory("Choose output_directory (root to contain CZI_metadata)");
  if (outRoot == null) { IJ.showMessage("Cancelled","No output directory selected."); return; }

  // Flat output dir
  var outMetaDir = new File(new File(outRoot), "CZI_metadata");
  if (!outMetaDir.exists()) outMetaDir.mkdirs();

  var totalFiles  = 0;
  var totalWrites = 0;

  traverse(new File(inRoot), function(file) {
    if (!file.isFile()) return;
    var name = String(file.getName()).toLowerCase();
    if (!name.endsWith(".czi")) return;

    var base = String(file.getName()).replaceFirst("\\.czi$", "");
    var outFile = uniqueFile(outMetaDir, base, ".tsv");

    var reader = new ZeissCZIReader();
    try {
      reader.setOriginalMetadataPopulated(true);
      reader.setMetadataFiltered(false);
      reader.setId(file.getAbsolutePath());

      var bw = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(outFile), StandardCharsets.UTF_8));
      bw.write("scope\tseries\tkey\tvalue");
      bw.newLine();

      // Global original metadata
      var gmeta = reader.getGlobalMetadata();
      if (gmeta != null) {
        var gkeys = gmeta.keySet().toArray();
        for (var i = 0; i < gkeys.length; i++) {
          var k = String(gkeys[i]);
          var v = gmeta.get(gkeys[i]);
          if (!isXMLLike(v)) {
            bw.write("Global\t\t" + tsvEscape(k) + "\t" + tsvEscape(String(v)));
            bw.newLine();
          }
        }
      }

      // Series original metadata
      var seriesCount = reader.getSeriesCount();
      for (var s = 0; s < seriesCount; s++) {
        reader.setSeries(s);
        var smeta = reader.getSeriesMetadata();
        if (smeta != null) {
          var skeys = smeta.keySet().toArray();
          for (var j = 0; j < skeys.length; j++) {
            var sk = String(skeys[j]);
            var sv = smeta.get(skeys[j]);
            if (!isXMLLike(sv)) {
              bw.write("Series\t" + s + "\t" + tsvEscape(sk) + "\t" + tsvEscape(String(sv)));
              bw.newLine();
            }
          }
        }
      }

      bw.close();
      IJ.log("Saved TSV: " + outFile.getAbsolutePath());
      totalWrites++;
      totalFiles++;
    } catch (e) {
      IJ.log("ERROR reading " + file.getAbsolutePath() + ": " + e);
      try { reader.close(); } catch (ee) {}
    } finally {
      try { reader.close(); } catch (ee2) {}
    }
  });

  IJ.showMessage("CZI Metadata TSV Export",
    "Processed " + totalFiles + " CZI file(s).\n" +
    "Wrote " + totalWrites + " TSV file(s) to:\n" +
    outMetaDir.getAbsolutePath());
})();

// ---------------- Helpers ----------------

// Recursive walk
function traverse(root, fn) {
  if (root == null || !root.exists()) return;
  var kids = root.listFiles();
  if (kids == null) return;
  for (var i = 0; i < kids.length; i++) {
    var f = kids[i];
    if (f.isDirectory()) traverse(f, fn);
    else fn(f);
  }
}

// Only filter XML-like values (everything else kept)
function isXMLLike(v) {
  if (v == null) return false;
  var s = String(v).trim();
  if (s.length == 0) return false;
  if (s.indexOf("<?xml") === 0) return true; // XML declaration
  // simple <tag>...</tag> pattern check
  if (s.indexOf("<") === 0 && s.indexOf("</") > 0 && s.indexOf(">") > 0) return true;
  return false;
}

// TSV escaping
function tsvEscape(s) {
  if (s == null) return "";
  s = String(s).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  s = s.replace(/\t/g, "\\t").replace(/\n/g, "\\n");
  return s;
}

// Ensure unique output filename: <dir>/<base>.ext, <base>_1.ext, <base>_2.ext, ...
function uniqueFile(dir, base, ext) {
  var f = new File(dir, base + ext);
  var idx = 1;
  while (f.exists()) {
    f = new File(dir, base + "_" + idx + ext);
    idx++;
  }
  return f;
}
