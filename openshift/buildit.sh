#! /bin/sh
oc start-build regapp-db -n regapp --from-dir=regapp-db --follow
