#!/usr/local/bin/python3
import gitlab_api


if __name__ == '__main__':
    obj = gitlab_api.GitlabAPI()
    # print([(user['name'], user['email']) for user in obj.get_users('@odoo.com')])
    # obj.project_mrs2csv(516) # MRS from ABSA
    # members_attributes = obj.get_members_attributes('vauxoo')
    # print(members_attributes)
    # members obj.get_members_grouped_by_access_level('vauxoo')
    # obj.delete_reporter_members('vauxoo')
    # obj.get_project_depends()
    # obj.get_project_variables()
    # custom_projects_branches = ["vauxoo/sbd@14.0", "vauxoo/tanner-common@15.0", "vauxoo/villagroup@15.0"]
    # custom_projects_branches = [
    #     "vauxoo/base-automation-python@13.0",
    #     "vauxoo/costarica@13.0",
    #     "vauxoo/costarica@14.0",
    #     "vauxoo/demo-enterprise@13.0",
    #     "vauxoo/ecuador@14.0",
    #     "vauxoo/hr-advanced@13.0",
    #     "vauxoo/hr-advanced@14.0",
    #     "vauxoo/l10n-mx-electronic-accounting@13.0",
    #     "vauxoo/l10n-mx-electronic-accounting@14.0",
    #     "vauxoo/l10n-mx-payroll@14.0",
    #     "vauxoo/mexico@13.0",
    #     "vauxoo/mexico@14.0",
    #     "vauxoo/vendor-bills@13.0",
    #     "vauxoo/xunnel-account@13.0",
    # ]
    # # custom_projects_branches = [
    # #     "vauxoo/l10n-mx-electronic-accounting@14.0"
    # # ]
    # created_mrs = obj.make_mr(
    #     custom_projects_branches,
    #     "[DUMMY] testing feature (autocreated) vauxoo/gitlab_tools#80",
    #     "Testing feature https://git.vauxoo.com/vauxoo/gitlab_tools/-/merge_requests/80",
    #     "gitlabtoolsmr80-moy",
    # )
    # print("MRs created: %s" % '\n'.join(created_mrs))

    # obj.get_pipeline_artifacts("vauxoo", ["15.0", "14.0", "13.0", "12.0"], ["odoo", "odoo_test"])
    # obj.get_project_files()

    # custom_projects_branches = [
    #     "absa/absa@12.0", "vauxoo/sbd@14.0", "vauxoo/tanner-common@15.0","vauxoo/villagroup@15.0","vauxoo/edicionesfiscales@15.0","vauxoo/mexico@15.0","vauxoo/trevly@15.0","vauxoo/instance@14.0",
    # ]
    # created_mrs = obj.make_mr(
    #     custom_projects_branches,
    #     "[REF] CI: Using new vx-ci (autocreated)",
    #     "Migrating to new CI tool https://git.vauxoo.com/devops/vxci\n\nPart of https://git.vauxoo.com/devops/vxci/-/issues/7",
    #     "vxci-moy",
    # )

    # custom_projects_branches = [
    #     "absa/absa@12.0",
    #     "qualifirst/qualifirst@13.0",
    #     "vauxoo/account-customer-invoice-split-discount@14.0",
    #     "vauxoo/bibo@15.0",
    #     "vauxoo/budget@14.0",
    #     "vauxoo/costarica@14.0",
    #     "vauxoo/edicionesfiscales@15.0",
    #     "vauxoo/instance@14.0",
    #     "vauxoo/mexico@14.0",
    #     "vauxoo/mexico@15.0",
    #     "vauxoo/performanceair@15.0",
    #     "vauxoo/samosol@15.0",
    #     "vauxoo/sbd@14.0",
    #     "vauxoo/sbdgroup@14.0",
    #     "vauxoo/tanner-common@15.0",
    #     "vauxoo/trevly@15.0",
    #     "vauxoo/typ@14.0",
    #     "vauxoo/villagroup@15.0",
    # ]
    # created_mrs = obj.make_mr(
    #     custom_projects_branches,
    #     "[REF] CI: Update project-template (autocreated)",
    #     "Now it is compatible with multiple pipelines with coverage combine",
    #     "vxci-cvrg-combine-moy",
    # )

    # custom_projects_branches = [
    #     # "absa/absa@12.0",
    #     # "qualifirst/qualifirst@13.0",
    #     "vauxoo/account-customer-invoice-split-discount@14.0",
    #     "vauxoo/bibo@15.0",
    #     "vauxoo/budget@14.0",
    #     "vauxoo/costarica@14.0",
    #     "vauxoo/edicionesfiscales@15.0",
    #     "vauxoo/instance@14.0",
    #     "vauxoo/mexico@14.0",
    #     "vauxoo/mexico@15.0",
    #     "vauxoo/performanceair@15.0",
    #     "vauxoo/samosol@15.0",
    #     "vauxoo/sbd@14.0",
    #     "vauxoo/sbdgroup@14.0",
    #     "vauxoo/tanner-common@15.0",
    #     "vauxoo/trevly@15.0",
    #     "vauxoo/typ@14.0",
    #     "vauxoo/villagroup@15.0",
    # ]
    # # custom_projects_branches = [
    # #     "vauxoo/edicionesfiscales@15.0",
    # #     "vauxoo/samosol@15.0",
    # #     "vauxoo/tanner-common@15.0",
    # #     "vauxoo/trevly@15.0",
    # #     "vauxoo/villagroup@15.0",
    # #     "qualifirst/qualifirst@15.0",
    # # ]
    # # custom_projects_branches = [i for i in custom_projects_branches if i.endswith("@15.0")]
    # # print('\n'.join(custom_projects_branches))
    # # created_mrs = obj.make_mr(
    # #     custom_projects_branches,
    # #     "[REF] patches: Remove odoo/odoo#98232 patch (autocreated)",
    # #     "It was already fixed from https://github.com/odoo/odoo/pull/99829",
    # #     "patches-rm98232-moy",
    # # )
    # created_mrs = obj.make_mr(
    #     custom_projects_branches,
    #     "[REF] CI: Add missing check_keys to get docker image from quay.io (autocreated)",
    #     "Related to https://git.vauxoo.com/vauxoo/project-template/-/merge_requests/101",
    #     "mr101-moy",
    # )
    # print("Created MRs:\n%s" % '\n'.join(created_mrs))
    # custom_projects_branches = [
    #     # "ircodoo/ircanada@14.0",
    #     "mexico/l10n-mx-edi-hr-expense@16.0",
    #     "qualifirst/qualifirst@13.0",
    #     "qualifirst/qualifirst@15.0",
    #     "vauxoo/account-customer-invoice-split-discount@14.0",
    #     "vauxoo/addons-vauxoo@15.0",
    #     "vauxoo/bantracking@16.0",
    #     "vauxoo/bibo@15.0",
    #     "vauxoo/budget@14.0",
    #     "vauxoo/cutting@15.0",
    #     "vauxoo/difacza@15.0",
    #     "vauxoo/edicionesfiscales@15.0",
    #     "vauxoo/facerindustrial@15.0",
    #     "vauxoo/honduras@15.0",
    #     "vauxoo/icm@15.0",
    #     "vauxoo/imesa@15.0",
    #     "vauxoo/instance@14.0",
    #     "vauxoo/l10n-mx-edi-40@13.0",
    #     "vauxoo/l10n-mx-payroll@14.0",
    #     "vauxoo/mexico-document@15.0",
    #     "vauxoo/nortenas@12.0",
    #     "vauxoo/opencfdi-server@15.0",
    #     "vauxoo/performance@12.0",
    #     "vauxoo/performance@14.0",
    #     "vauxoo/performance@15.0",
    #     "vauxoo/performanceair@15.0",
    #     "vauxoo/psadurango@15.0",
    #     "vauxoo/python-jasper-report@12.0",
    #     "vauxoo/samosol@15.0",
    #     "vauxoo/sbd@14.0",
    #     "vauxoo/sbdgroup@14.0",
    #     "vauxoo/tanner-common@15.0",
    #     "vauxoo/tanner@15.0",
    #     "vauxoo/trevly@15.0",
    #     "vauxoo/typ@14.0",
    # ]
    # # obj.get_project_files()
    # created_mrs = obj.make_mr(
    #     custom_projects_branches,
    #     "[REF] autofixes: Apply future autofixes\n"
    #     "Autofixes new version are creating changes",
    #     "autofixes-moy",
    #     run_pre_commit_vauxoo=True,
    #     task_id="1147",  # Similar to LINT xD
    # )
    # print("MRs created: %s" % '\n'.join(created_mrs))
    non_ascii = r"[^\x00-\x7F]"
    print(obj.look_for_filename(fname_regex=non_ascii, only_default_branch=True))
