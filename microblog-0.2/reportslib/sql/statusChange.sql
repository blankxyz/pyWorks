SELECT
  whos.realname            AS name,
  count(hisResoled.bug_id) AS resoled,
  count(hisClose.bug_id)   AS closed,
  count(hisReopen.bug_id)  AS reopened /**/
FROM
  (SELECT *
   FROM profiles) AS whos
  LEFT JOIN
  (SELECT *
   FROM bugs_activity
   WHERE fieldid = '9' AND removed = 'NEW' AND added IN ('RESOLVED') AND TO_DAYS(bug_when) = TO_DAYS('2015-12-03')) AS hisResoled
    ON whos.userid = hisResoled.who
  LEFT JOIN
  (SELECT *
   FROM bugs_activity
   WHERE fieldid = '9' AND removed = 'RESOLVED' AND added IN ('VERIFIED', 'CLOSED') AND TO_DAYS(bug_when) = TO_DAYS('2015-12-03')) AS hisClose
    ON whos.userid = hisClose.who
  LEFT JOIN
  (SELECT *
   FROM bugs_activity
   WHERE fieldid = '9' AND removed = 'RESOLVED' AND added IN ('REOPENED') AND TO_DAYS(bug_when) = TO_DAYS('2015-12-03')) AS hisReopen
    ON whos.userid = hisReopen.who
GROUP BY whos.userid