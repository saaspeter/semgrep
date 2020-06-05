#!/bin/bash

# Use static linking if platform allows.
#
if [[ -e /etc/alpine-release ]]; then
  echo "(-ccopt -static)" > flags.sexp
else
  echo "( :standard )" > flags.sexp
fi
