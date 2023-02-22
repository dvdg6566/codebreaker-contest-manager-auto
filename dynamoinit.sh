aws dynamodb put-item --table-name codebreakercontest-global-counters \
--item '{"counterId": {"S": "submissionId"}, "value": {"N": "0"}}'

# TODO: Add thing to initialise first user

aws dynamodb put-item --table-name codebreakercontest-users \
--item '{"username": {"S": "0rang3"}, "role": {"S": "admin"}, "problemScores": {"M" : {}}, "fullname": {"S": "Default admin"}, "contest": {"S": ""}}'