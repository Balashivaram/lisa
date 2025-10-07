from .azfwUtility import installAzureCLI


def setup_azureFirewall(firewallNode, log):
    GsaTestStorageBlobReaderIdentity = ""
    
    

    result = firewallNode.execute(f"sudo az login --identity --resource-id {GsaTestStorageBlobReaderIdentity}", sudo=True) #Done
    log.info("Result for logging into azure:", result) #Done
    result = firewallNode.execute("sudo az storage blob download --auth-mode login --account-name gsateststorage -c app -n app/app-15432201/bootstrap.tar -f /tmp/bootstrap.tar") #Done
    log.info("Result for downloading bootstrap.tar:", result) #Done
    result = firewallNode.execute("sudo chmod 666 /tmp/bootstrap.tar", sudo=True) #Done
    log.info("Result for changing permissions of bootstrap.tar:", result) #Done
    result = firewallNode.execute("sudo chmod -R 777 /tmp/bootstrap/", sudo=True) #Done
    log.info("Result for changing permissions of /tmp/bootstrap/:", result) #Done
    result = firewallNode.execute("mkdir -p /tmp/bootstrap/ && tar -xvf /tmp/bootstrap.tar -C /tmp/bootstrap/", sudo=True) #Done
    log.info("Result for extracting bootstrap.tar:", result)
    log.info("This is the environment: ", environment)
    GsaTestStorageBlobReaderIdentity = ""
    fwcreationconfigfileidentity = ""
    log.info("Setting up Azure CLI....")
    firewallNode = cast(RemoteNode, environment.nodes[0])
    firewallNode.execute("sudo tdnf install -y azure-cli", sudo=True)

    try:
        result = firewallNode.execute(f"az login --identity --resource-id {GsaTestStorageBlobReaderIdentity}")
        log.info('Successfully logged into lisa storage', result)
        
        #download necessary files from blob storage
        files = ["mdsd.service", "mock_statsd.service", "mock_statsd.py", "mock_mdsd", "install_runtime_deps.sh", "importdatafromjson.py", "cseparams.json", "bootstrap_geneva.sh"]
        for file in files:
            firewallNode.execute(f"az storage blob download --auth-mode login --account-name lisatestresourcestorage  -c fwcreateconfigfiles -n {file} -f /tmp/{file}")

        result = firewallNode.execute("chmod 666 /tmp/mdsd.service /tmp/mock_statsd.service /tmp/mock_statsd.py /tmp/mock_mdsd /tmp/install_runtime_deps.sh /tmp/importdatafromjson.py bootstrap_geneva.sh", sudo=True)
        log.info("Changed permissions for bootstrap.tar", result)

        result = firewallNode.execute("chmod -R 777 /tmp/mdsd.service /tmp/mock_statsd.service /tmp/mock_statsd.py /tmp/mock_mdsd /tmp/install_runtime_deps.sh /tmp/importdatafromjson.py bootstrap_geneva.sh", sudo=True)
        log.info("Changed permissions for bootstrap.tar", result)

        #Generate mdsMetadata.txt file
        result = firewallNode.execute("python3 /tmp/importdatafromjson.py", sudo=True)
        log.info("Successfully generated mdsMetadata.txt", result)

        #Upload the mdsMetadata.txt file to blob storage
        result = firewallNode.execute("az storage blob upload --auth-mode login --account-name lisatestresourcestorage  -c fwcreateconfigfiles -n mdsMetadata.txt -f /tmp/mdsMetadata.txt", sudo=True) # Done 
        log.info("Successfully uploaded mdsMetadata.txt to blob storage", result) # Done

        result = firewallNode.execute("bash -x /tmp/install_runtime_deps.sh", sudo=True)
        log.info("Successfully executed install_runtime_deps.sh", result.stdout)
        firewallNode.execute("mv /tmp/mdsd.service /etc/systemd/system/mdsd.service", sudo=True)
        firewallNode.execute("mv /tmp/mock_statsd.service /etc/systemd/system/mock_statsd.service", sudo=True)
        firewallNode.execute("mv /tmp/mock_statsd.py /opt/mock_statsd.py", sudo=True)
        firewallNode.execute("mv /tmp/mock_mdsd /opt/mock_mdsd", sudo=True)
        firewallNode.execute("useradd -M -e 2100-01-01 azfwuser", sudo=True)
        # Reload daemon 
        result = firewallNode.execute("sudo systemctl daemon-reload", sudo=True)
        log.info("Daemon reloaded successfully", result)
        #Restart mdsd and mdsd.statsd service
        result = firewallNode.execute("sudo systemctl restart mock_statsd.service", sudo=True)
        result = firewallNode.execute("sudo systemctl restart mdsd.service", sudo=True)
        
        # Continue with your blob download and other operations
        result = firewallNode.execute("az storage blob download --auth-mode login --account-name gsateststorage -c app -n app/app-15817278/bootstrap.tar -f /tmp/bootstrap.tar") #Done
        log.info("Successfully downloaded bootstrap.tar", result) #Done

        result = firewallNode.execute("sudo chmod 666 /tmp/bootstrap.tar", sudo=True) #Done
        log.info("Changed permissions for bootstrap.tar", result) #Done

        result = firewallNode.execute("sudo chmod -R 777 /tmp/bootstrap.tar", sudo=True) #Done
        log.info("Changed permissions for bootstrap.tar", result) #Done


        result = firewallNode.execute("mkdir /tmp/bootstrap/") #Done
        log.info("Created Directory /tmp/bootstrap/", result)

        result = firewallNode.execute("python -m ensurepip", sudo=True) #done
        log.info("Successfully installed psutil", result)
        result = firewallNode.execute('export PATH="$PATH:/home/lisatest/.local/bin"') #done
        log.info("Added /home/lisatest/.local/bin to PATH", result)
        result = firewallNode.execute(" python -m pip install psutil", sudo=True) #Done
        log.info("Successfully installed psutil", result)

        result = firewallNode.execute("tar -xvf /tmp/bootstrap.tar -C /tmp/bootstrap/", sudo=True) #Done
        if "10-mdsd.conf" in result.stdout:
            log.info("Successfully extracted bootstrap.tar")

        result = firewallNode.execute("mv /tmp/bootstrap_geneva.sh /tmp/bootstrap/drop/vmss/bootstrap_geneva.sh", sudo=True) #Done

        result = firewallNode.execute("sed -i '461d' /tmp/bootstrap/drop/vmss/azfw_common.sh", sudo=True) #Done
        result = firewallNode.execute("sed -i '79d' /tmp/bootstrap/drop/vmss/bootstrap.sh", sudo=True)    #Done

        json_value = {
                "RULE_CONFIG_URL": "https://lisatestresourcestorage.blob.core.windows.net/fwcreateconfigfiles/ruleConfig.json",
                "RULE_CONFIG_NAME": "",
                "SETTINGS_URL": "https://lisatestresourcestorage.blob.core.windows.net/fwcreateconfigfiles/mdsMetadata.txt",
                "GENEVATHUMBPRINT": "",
                "FQDN_TAGS_CONFIG_URL": "https://lisatestresourcestorage.blob.core.windows.net/fwcreateconfigfiles/defaultfqdntags.json",
                "SERVICE_TAGS_CONFIG_URL": "https://lisatestresourcestorage.blob.core.windows.net/fwcreateconfigfiles/servicetags.json",
                "WEB_CATEGORIES_CONFIG_URL": "https://lisatestresourcestorage.blob.core.windows.net/fwcreateconfigfiles/defaultwebcategories.json",
                "IDPS_RULES_CONFIG_URL": "https://lisatestresourcestorage.blob.core.windows.net/fwcreateconfigfiles/rules.tar.gz",
                "IDPS_RULES_OVERRIDES_URL": "https://lisatestresourcestorage.blob.core.windows.net/fwcreateconfigfiles/instrusionsystemoverrides.json",
                "INTERFLOW_KEY": "",
                "WEB_CATEGORIZATION_VENDOR_LICENSE_KEY": "",
                "AAD_TENANT_ID": "",
                "AAD_CLIENT_ID": "",
                "AAD_SECRET": "",
                "NUMBER_PUBLIC_IPS": 1,
                "NUMBER_PORTS_PER_PUBLIC_IP": 2496,
                "DATA_SUBNET_PREFIX": "10.0.0.0/24",
                "DATA_SUBNET_PREFIX_IPV6": "",
                "MGMT_SUBNET_PREFIX": "",
                "ROUTE_SERVICE_CONFIG_URL": None,
                "TENANT_KEYVAULT_URL": "https://fwcreationkeyvault.vault.azure.net/",
                "TENANT_IDENTITY_RESOURCE_ID": "",
                "REGIONAL_KEYVAULT_URL": "https://fwcreationkeyvault.vault.azure.net/",
                "REGIONAL_IDENTITY_RESOURCE_ID": "",
                "NOSNAT_IPPREFIXES_CONFIG_SAS_URL": None,
                "NOSNAT_IS_AUTO_LEARN_ENABLED": None
            }

        json_str = json.dumps(json_value)
        # escaped_json = json_str.replace('"', '\\"')
        command = f"/tmp/bootstrap/drop/vmss/bootstrap.sh '{json_str}'"
        result = firewallNode.execute(f"bash -x {command}", sudo=True)
        log.info("Successfully executed bootstrap.sh", result)
