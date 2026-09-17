// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

contract LifecycleTracker {
    enum State { None, Active, Completed, Failed, Revoked }

    struct Instance {
        bytes32 intentHash;
        bytes32 modelHash;
        bytes32 policyHash;
        State state;
        uint64 transitionCount;
        address creator;
    }

    struct Transition {
        State previousState;
        bytes32 actionHash;
        bytes32 paymentHash;
        bytes32 evidenceHash;
        State nextState;
    }

    mapping(bytes32 => Instance) private instances;
    mapping(bytes32 => mapping(uint64 => Transition)) private transitions;

    event InstanceCreated(bytes32 indexed instanceId, address indexed creator, bytes32 intentHash, bytes32 modelHash, bytes32 policyHash);
    event TransitionRecorded(bytes32 indexed instanceId, uint64 indexed transitionNo, State previousState, bytes32 actionHash, bytes32 paymentHash, bytes32 evidenceHash, State nextState);
    event InstanceFinalized(bytes32 indexed instanceId, State finalState);

    error InstanceExists();
    error UnknownInstance();
    error Unauthorized();
    error TerminalInstance();
    error InvalidState();
    error InvalidCommitment();

    function createInstance(bytes32 instanceId, bytes32 intentHash, bytes32 modelHash, bytes32 policyHash) external {
        if (instances[instanceId].creator != address(0)) revert InstanceExists();
        if (instanceId == bytes32(0) || intentHash == bytes32(0) || modelHash == bytes32(0) || policyHash == bytes32(0)) revert InvalidCommitment();
        instances[instanceId] = Instance(intentHash, modelHash, policyHash, State.Active, 0, msg.sender);
        emit InstanceCreated(instanceId, msg.sender, intentHash, modelHash, policyHash);
    }

    function recordTransition(
        bytes32 instanceId,
        State previousState,
        bytes32 actionHash,
        bytes32 paymentHash,
        bytes32 evidenceHash,
        State nextState
    ) external {
        Instance storage inst = _authorized(instanceId);
        if (inst.state != State.Active) revert TerminalInstance();
        if (previousState != inst.state) revert InvalidState();
        if (nextState != State.Active) revert InvalidState(); // paid transitions in the prototype are Active -> Active
        if (actionHash == bytes32(0) || paymentHash == bytes32(0) || evidenceHash == bytes32(0)) revert InvalidCommitment();

        uint64 n = inst.transitionCount;
        transitions[instanceId][n] = Transition(previousState, actionHash, paymentHash, evidenceHash, nextState);
        inst.transitionCount = n + 1;
        inst.state = nextState;
        emit TransitionRecorded(instanceId, n, previousState, actionHash, paymentHash, evidenceHash, nextState);
    }

    function finalizeInstance(bytes32 instanceId, State finalState) external {
        Instance storage inst = _authorized(instanceId);
        if (inst.state != State.Active) revert TerminalInstance();
        if (finalState != State.Completed && finalState != State.Failed && finalState != State.Revoked) revert InvalidState();
        inst.state = finalState;
        emit InstanceFinalized(instanceId, finalState);
    }

    function getInstance(bytes32 instanceId) external view returns (Instance memory) {
        Instance memory inst = instances[instanceId];
        if (inst.creator == address(0)) revert UnknownInstance();
        return inst;
    }

    function getTransition(bytes32 instanceId, uint64 transitionNo) external view returns (Transition memory) {
        Instance memory inst = instances[instanceId];
        if (inst.creator == address(0)) revert UnknownInstance();
        if (transitionNo >= inst.transitionCount) revert InvalidState();
        return transitions[instanceId][transitionNo];
    }

    function _authorized(bytes32 instanceId) internal view returns (Instance storage inst) {
        inst = instances[instanceId];
        if (inst.creator == address(0)) revert UnknownInstance();
        if (inst.creator != msg.sender) revert Unauthorized();
    }
}
