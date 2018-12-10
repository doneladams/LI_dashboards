SELECT DISTINCT cc.licensenumber,
  lt.name LicenseType,
  (CASE
    WHEN cc.mostrecentissuedate IS NOT NULL
    THEN Extract(MONTH FROM cc.mostrecentissuedate)
      || '/'
      ||Extract(DAY FROM cc.mostrecentissuedate)
      || '/'
      || Extract(YEAR FROM cc.mostrecentissuedate)
    WHEN cc.mostrecentissuedate IS NULL
    THEN NULL
  END) mostrecentissuedate,
  (CASE
    WHEN cc.MostRecentCompletenessCheck IS NOT NULL
    THEN Extract(MONTH FROM cc.MostRecentCompletenessCheck)
      || '/'
      ||Extract(DAY FROM cc.MostRecentCompletenessCheck)
      || '/'
      || Extract(YEAR FROM cc.MostRecentCompletenessCheck)
    WHEN cc.MostRecentCompletenessCheck IS NULL
    THEN NULL
  END) MostRecentCompletenessCheck,
  cc.MostRecentCompletenessCheck MostRecentCCField,
  (CASE
    WHEN lg.expirationdate IS NOT NULL
    THEN Extract(MONTH FROM lg.expirationdate)
      || '/'
      ||Extract(DAY FROM lg.expirationdate)
      || '/'
      || Extract(YEAR FROM lg.expirationdate)
    WHEN lg.expirationdate IS NULL
    THEN NULL
  END) expirationdate,
  (CASE
    WHEN inspe.InspectionCreatedDate IS NOT NULL
    THEN Extract(MONTH FROM inspe.InspectionCreatedDate)
      || '/'
      ||Extract(DAY FROM inspe.InspectionCreatedDate)
      || '/'
      || Extract(YEAR FROM inspe.InspectionCreatedDate)
    WHEN inspe.InspectionCreatedDate IS NULL
    THEN NULL
  END) InspectionCreatedDate,
  (CASE
    WHEN inspe.ScheduledInspectionDate IS NOT NULL
    THEN Extract(MONTH FROM inspe.ScheduledInspectionDate)
      || '/'
      ||Extract(DAY FROM inspe.ScheduledInspectionDate)
      || '/'
      || Extract(YEAR FROM inspe.ScheduledInspectionDate)
    WHEN inspe.ScheduledInspectionDate IS NULL
    THEN NULL
  END) ScheduledInspectionDate,
  (CASE
    WHEN inspe.InspectionCompletedDate IS NOT NULL
    THEN Extract(MONTH FROM inspe.InspectionCompletedDate)
      || '/'
      ||Extract(DAY FROM inspe.InspectionCompletedDate)
      || '/'
      || Extract(YEAR FROM inspe.InspectionCompletedDate)
    WHEN inspe.InspectionCompletedDate IS NULL
    THEN NULL
  END) InspectionCompletedDate
FROM lmscorral.bl_licensetype lt,
  lmscorral.bl_licensegroup lg,
  (SELECT l.licensenumber,
    l.LICENSETYPEOBJECTID,
    l.LICENSEGROUPOBJECTID,
    l.MOSTRECENTISSUEDATE,
    MAX(p.datecompleted) MostRecentCompletenessCheck
  FROM lmscorral.bl_license l,
    lmscorral.bl_joblicensexref x,
    api.processes p,
    api.processtypes pt
  WHERE l.objectid    = x.licenseobjectid
  AND x.jobid         = p.jobid
  AND p.processtypeid = pt.processtypeid
  AND pt.processtypeid LIKE '1239327'
  AND p.datecompleted IS NOT NULL
  GROUP BY l.licensenumber,
    l.LICENSETYPEOBJECTID,
    l.LICENSEGROUPOBJECTID,
    l.MOSTRECENTISSUEDATE
  ) cc,
  (SELECT DISTINCT insp.LicenseNumber,
    insp.createddate InspectionCreatedDate,
    insp.scheduledInspectiondate ScheduledInspectionDate,
    insp.completeddate InspectionCompletedDate
  FROM
    (SELECT lic.ExternalFileNum LicenseNumber,
      ins.createddate,
      ins.scheduledInspectiondate,
      ins.completeddate
    FROM QUERY.J_BL_INSPECTION ins,
      QUERY.R_BL_LICENSEINSPECTION li,
      query.o_bl_license lic
    WHERE ins.ObjectId     = li.InspectionId
    AND li.LicenseId       = lic.ObjectId
    AND ins.CompletedDate IS NULL
    UNION
    SELECT lic.ExternalFileNum LicenseNumber,
      ins.createddate,
      ins.scheduledInspectiondate,
      ins.completeddate
    FROM QUERY.J_BL_INSPECTION ins,
      query.r_bl_applicationinspection api,
      query.j_bl_application ap,
      query.r_bl_application_license apl,
      query.o_bl_license lic
    WHERE ins.ObjectId      = api.InspectionId
    AND api.ApplicationId   = ap.ObjectId
    AND ap.ObjectId         = apl.ApplicationObjectId
    AND apl.LicenseObjectId = lic.ObjectId
    AND ins.CompletedDate  IS NULL
    UNION
    SELECT lic.ExternalFileNum LicenseNumber,
      ins.createddate,
      ins.scheduledInspectiondate,
      ins.completeddate
    FROM QUERY.J_BL_INSPECTION ins,
      query.r_bl_amendrenewinspection ari,
      query.j_bl_amendrenew ar,
      QUERY.R_BL_AMENDRENEW_LICENSE arl,
      query.o_bl_license lic
    WHERE ins.objectid     = ari.InspectionId
    AND ari.AmendRenewId   = ar.JobId
    AND ar.ObjectId        = arl.AmendRenewId
    AND arl.LicenseId      = lic.ObjectId
    AND ins.CompletedDate IS NULL
    ) insp
  ) inspe
WHERE cc.licensenumber      = inspe.LicenseNumber (+)
AND cc.licensetypeobjectid  = lt.objectid (+)
AND cc.licensegroupobjectid = lg.objectid (+)