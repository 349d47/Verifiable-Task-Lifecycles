// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import "../src/LifecycleTracker.sol";

contract LifecycleTrackerTest {
    LifecycleTracker tracker;
    bytes32 constant ID = keccak256("instance");
    bytes32 constant I = keccak256("intent");
    bytes32 constant M = keccak256("model");
    bytes32 constant P = keccak256("policy");

    function setUp() public { tracker = new LifecycleTracker(); }

    function testCreateStartsActive() public {
        tracker.createInstance(ID, I, M, P);
        LifecycleTracker.Instance memory inst = tracker.getInstance(ID);
        require(inst.state == LifecycleTracker.State.Active);
        require(inst.transitionCount == 0);
        require(inst.creator == address(this));
    }

    function testRecordTransitionIncrementsCount() public {
        tracker.createInstance(ID, I, M, P);
        tracker.recordTransition(ID, LifecycleTracker.State.Active, keccak256("a"), keccak256("p"), keccak256("e"), LifecycleTracker.State.Active);
        LifecycleTracker.Instance memory inst = tracker.getInstance(ID);
        require(inst.transitionCount == 1);
        LifecycleTracker.Transition memory t = tracker.getTransition(ID, 0);
        require(t.actionHash == keccak256("a"));
    }

    function testFinalizeCompleted() public {
        tracker.createInstance(ID, I, M, P);
        tracker.finalizeInstance(ID, LifecycleTracker.State.Completed);
        require(tracker.getInstance(ID).state == LifecycleTracker.State.Completed);
    }

    function testCannotRecordTerminalTransitionAfterFinalization() public {
        tracker.createInstance(ID, I, M, P);
        tracker.finalizeInstance(ID, LifecycleTracker.State.Completed);
        try tracker.recordTransition(ID, LifecycleTracker.State.Completed, keccak256("a"), keccak256("p"), keccak256("e"), LifecycleTracker.State.Active) {
            revert("expected revert");
        } catch {}
    }
}
