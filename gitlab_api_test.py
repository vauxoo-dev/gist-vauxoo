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

    custom_projects_branches = [
        "absa/absa@12.0", "vauxoo/sbd@14.0", "vauxoo/tanner-common@15.0","vauxoo/villagroup@15.0","vauxoo/edicionesfiscales@15.0","vauxoo/mexico@15.0","vauxoo/trevly@15.0","vauxoo/instance@14.0",
    ]
    created_mrs = obj.make_mr(
        custom_projects_branches,
        "[REF] CI: Using new vx-ci (autocreated)",
        "Migrating to new CI tool https://git.vauxoo.com/devops/vxci\n\nPart of https://git.vauxoo.com/devops/vxci/-/issues/7",
        "vxci-moy",
    )
