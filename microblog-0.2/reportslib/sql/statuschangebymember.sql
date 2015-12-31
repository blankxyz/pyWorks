SELECT
  usr.realname           AS name,
  hisNew.who             AS userid,
  count(hisNew.who)      AS new2resolved,
  count(hisResolved.who) AS resolved2verified
FROM
  (SELECT *
   FROM profiles
   WHERE `show` = '1') AS usr
  LEFT JOIN
  (SELECT *
   FROM bugs_activity
   WHERE fieldid = '9' AND removed = 'NEW' AND added IN ('RESOLVED') AND TO_DAYS(bug_when) = TO_DAYS('2015-11-09')) AS hisNew
    ON
      usr.userid = hisNew.who
  LEFT JOIN
  (SELECT *
   FROM bugs_activity
   WHERE fieldid = '9' AND removed = 'RESOLVED' AND added IN ('VERIFIED') AND TO_DAYS(bug_when) = TO_DAYS('2015-11-09')) AS hisResolved
    ON
      usr.userid = hisResolved.who
GROUP BY
  usr.userid