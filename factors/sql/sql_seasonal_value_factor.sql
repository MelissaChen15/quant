

--表1： LC_MainIndexNew
select t2.SecuCode,t1.EndDate,t1.EnterpriseFCFPS,t1.EPSTTM
 from LC_MainIndexNew t1
inner join SecuMain t2
on t1.CompanyCode=t2.CompanyCode
where (t2.SecuMarket='83' or t2.SecuMarket='90') and (t2.SecuCode='000001' or t2.SecuCode='000002')order by SecuCode


