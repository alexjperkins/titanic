raft:
	@echo "--- starting raft server ---"
	docker-compose -f local.raft.yml up raft_0

rafts:
	@echo "--- starting raft servers ---"
	docker-compose -f local.raft.yml up --build


