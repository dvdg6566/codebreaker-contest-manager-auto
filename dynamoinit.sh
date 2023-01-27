aws dynamodb put-item --table-name codebreakercontest-global-counters \
--item '{"counterId": {"S": "submissionId"}, "value": {"N": "0"}}'

aws dynamodb put-item --table-name codebreakercontest-global-counters \
--item '{"counterId": {"S": "clarificationId"}, "value": {"N": "0"}}'

# TODO: Add thing to initialise first user