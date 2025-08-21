## Azure Automated Red Team - Azure Foundry ##
This notebook -red.ipynb is to demonstrate the use of Automated Red Teaming in Azure Foundry

-- The requirements for this is role assignments in the Azure Foundry Project (Storage Blob Data Contributor) - to the underlying data store this is likely the attached Azure Storage Account.
This can be ran in private endpoints but ensure you have line of sight from the Project to Storage Account and Execution, the code will have the use of a .env this is not committed to the repository but ensure you follow if your using the RedTeam() object that you denote azure_deployment parameter when executing a scan this appears to be mixed up with independent use of PyRiT.
