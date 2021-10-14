# Managing secrets with kubeseal

* Install controller
  * Minikube use files checked in
  * Openshift - ??

* Create custom key pair
  * `https://github.com/bitnami-labs/sealed-secrets/blob/main/docs/bring-your-own-certificates.md`
  * Setup convenience envars
      export PRIVATEKEY="mytls.key" <!-- pragma: allowlist secret -->
      export PUBLICKEY="mytls.crt"
      export NAMESPACE="sealed-secrets"
      export SECRETNAME="mycustomkeys" <!-- pragma: allowlist secret -->
  * Create the openssl key
    * openssl req -x509 -nodes -newkey rsa:4096 -keyout "$PRIVATEKEY" -out \
        "$PUBLICKEY" -subj "/CN=sealed-secret/O=sealed-secret"
  * Create and persist the custom keypair as a secret.yml file
    * kubectl -n "$NAMESPACE" create secret tls "$SECRETNAME" \
        --cert="$PUBLICKEY" --key="$PRIVATEKEY"
    * kubectl -n sealed-secrets get secret mycustomkeys -o yaml > customkeys.yml
    * edit customkeys.yml and add the label
      * sealedsecrets.bitnami.com/sealed-secrets-key: active
      * this tells the controller to try this key as well
    * Apply the yaml to add the label (and test)
  * Save the keypair and the secret file someplace wicked secure
    * NOT ON CLUSTER - this is a backup
    * NOT ON GITHUB - yeah don't do that...

* Encrypt a secret file using the custom key
  * Annotate your secret to tell controller to manage
    annotations:
        sealedsecrets.bitnami.com/managed: "true"
  * kubeseal --cert $PUBLICKEY -o yaml < testsecret.yml > testsecret_sealed.yml
    * specify namespace in secret
    * sealed secret can only be applied in the namespace declared in the secret
  * Add sealed secret to namespace specified in secret

* Apply sealed secret
  * Just like any other yaml...
  * kubectl apply -f -n NAMESPACE_OF_SECRET -f testsecret_sealed.yml

* Edit sealed secret
  * Create a secret fragment with the same name and namespace as the original secret
  * Encrypt the fragment as described above
  * Cut the keys that you want out of the generated file and paste into the secret
  you want to edit
  * Done

* Decrypt a sealed secret with local keys
  * Note that you can always browse the values on the cluster but if the cluster
  is gone bye bye...
  * cat testsecret_sealed.yml | kubeseal --recovery-unseal \
      --recovery-private-key $PRIVATEKEY
