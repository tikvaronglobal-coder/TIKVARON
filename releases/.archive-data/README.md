# v0.2.0 release archive

The release ZIP is stored as ordered Base64 text segments in this directory so it can be committed using GitHub's text-only content interface. Workflows concatenate the `.part-*` files in lexical order, decode the ZIP, run `unzip -t`, and install the resulting release. Do not edit individual parts; publish a new versioned archive if the release changes.
